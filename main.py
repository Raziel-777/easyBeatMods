import os
import shutil
import tempfile
import zipfile

import requests

PUBLIC_CDN_BASE_URL = "https://bbm.saera.gay/cdn"
BASE_URL = 'https://beatmods.com'
GAME_VERSION = '1.40.0'
API_URL = f'/api/mods?gameName=BeatSaber&gameVersion={GAME_VERSION}&status=verified&platform=universalpc'
MODS_URL = f"{BASE_URL}{API_URL}"
MOD_URL = f"{BASE_URL}/api/mods/"
MOD_VERSION_URL = f"{BASE_URL}/api/modversions/"
MODS = ['bsipa', 'songcore', 'betterpause', 'heck', 'chroma', 'bettersonglist', 'bettersongsearch',
        'noodleextensions', 'playlistmanager', 'songplayhistory', 'customsaberslite', 'custom avatars', 'camera2']
MODS_DIRECTORY = './mods'
ARCHIVE = './mods_archive'
ALREADY_DOWNLOADED = []
ALREADY_DOWNLOADED_WITH_VERSION = []
SKIP_VERIFIED = True


def download_mod(mod_name, mod_version, mod_dir_path, temp_dir):
    if mod_name is None:
        mod_id = mod_version['modId']
        URL = f"{MOD_URL}{mod_id}"
        response = requests.get(f"{URL}")
        response.raise_for_status()
        mod_name = response.json()['mod']['info']['name'].lower()
        print(f'dep -------> {mod_name}')
    if mod_name not in ALREADY_DOWNLOADED:
        zip_hash = mod_version["zipHash"]
        zip_url = f'{PUBLIC_CDN_BASE_URL}/mod/{zip_hash}.zip'
        mod_resp = requests.get(zip_url, stream=True)
        mod_resp.raise_for_status()
        zip_path = os.path.join(temp_dir, "archive_temp.zip")
        with open(zip_path, "wb") as file:
            for chunk in mod_resp.iter_content(chunk_size=8192):
                file.write(chunk)
        with zipfile.ZipFile(zip_path, mode="r") as zipf:
            zipf.extractall(mod_dir_path)
        os.remove(zip_path)
        ALREADY_DOWNLOADED.append(mod_name)
        ALREADY_DOWNLOADED_WITH_VERSION.append(f'{mod_name} {mod_version["modVersion"]}')


if __name__ == '__main__':
    if os.path.exists(MODS_DIRECTORY):
        shutil.rmtree(MODS_DIRECTORY)
    os.makedirs(MODS_DIRECTORY)

    with tempfile.TemporaryDirectory() as temp_dir:
        all_mods_resp = requests.get(f"{MODS_URL}")
        all_mods_resp.raise_for_status()
        all_mods = all_mods_resp.json()['mods']
        MODS_LOWER = [mod.lower() for mod in MODS]
        for mod in all_mods:
            name = mod['mod']['name'].lower()
            mod_id = mod['mod']['id']
            if name in MODS_LOWER and name not in ALREADY_DOWNLOADED:
                print(name)
                mod_url = f"{MOD_URL}{mod_id}"
                response = requests.get(f"{mod_url}")
                response.raise_for_status()
                mod_versions = response.json()['mod']['versions']
                for mod_version in mod_versions[::-1]:
                    if SKIP_VERIFIED or mod_version['status'] == 'verified':
                        download_mod(name, mod_version, MODS_DIRECTORY, temp_dir)
                        for dependency in mod_version['dependencies']:
                            dependency_url = f"{MOD_VERSION_URL}{dependency}?&raw=true"
                            resp = requests.get(f"{dependency_url}")
                            resp.raise_for_status()
                            dependency_mod_version = resp.json()['modVersion']
                            download_mod(None, dependency_mod_version, MODS_DIRECTORY, temp_dir)
                        break

    shutil.make_archive(ARCHIVE, 'zip', MODS_DIRECTORY)
    for el in ALREADY_DOWNLOADED_WITH_VERSION:
        print(el)
