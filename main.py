import os
import shutil
import tempfile
import zipfile

import requests

BASE_URL = 'https://beatmods.com'
GAME_VERSION = '1.40'
API_URL = f'/api/v1/mod?status=approved&gameVersion={GAME_VERSION}'
MODS_URL = f"{BASE_URL}{API_URL}"
MODS = ['BSIPA', 'SongCore', 'BetterPause', 'Custom Platforms', '_Heck', 'Chroma', 'BetterSongList',
        'BetterSongSearch', 'NoodleExtensions', 'PlaylistManager', 'SongPlayHistory', 'CustomSabersLite',
        'Custom Avatars']
MODS_DIRECTORY = './mods'
ARCHIVE = './mods_archive'


def download_mod(url, mod_dir_path, temp_dir):
    mod_resp = requests.get(url, stream=True)
    mod_resp.raise_for_status()
    zip_path = os.path.join(temp_dir, "archive_temp.zip")
    with open(zip_path, "wb") as file:
        for chunk in mod_resp.iter_content(chunk_size=8192):
            file.write(chunk)
    with zipfile.ZipFile(zip_path, mode="r") as zipf:
        zipf.extractall(mod_dir_path)
    os.remove(zip_path)


if __name__ == '__main__':
    already_downloaded = []
    already_downloaded_with_version = []
    if os.path.exists(MODS_DIRECTORY):
        shutil.rmtree(MODS_DIRECTORY)
    os.makedirs(MODS_DIRECTORY)

    with tempfile.TemporaryDirectory() as temp_dir:
        for mod in MODS:
            URL = f"{MODS_URL}&name={mod}&sort=version&sortDirection=-1"
            response = requests.get(f"{URL}")
            response.raise_for_status()
            versions = response.json()
            if versions:
                latest_version = versions[0]
                for download in latest_version['downloads']:
                    if download['type'] == 'universal':
                        download_mod(f'{BASE_URL}{download["url"]}', MODS_DIRECTORY, temp_dir)
                        already_downloaded.append(mod)
                        already_downloaded_with_version.append(f'{mod} {latest_version["version"]}')
                    else:
                        raise Exception(f'not universal {mod}')
                for dependency in latest_version['dependencies']:
                    if dependency['name'] not in already_downloaded:
                        for download in dependency['downloads']:
                            if download['type'] == 'universal':
                                download_mod(f'{BASE_URL}{download["url"]}', MODS_DIRECTORY, temp_dir)
                                already_downloaded.append(dependency['name'])
                                already_downloaded_with_version.append(f'{dependency["name"]} {dependency["version"]}')
                            else:
                                raise Exception(f'not universal {dependency["name"]}')
    shutil.make_archive(ARCHIVE, 'zip', MODS_DIRECTORY)
    for el in already_downloaded_with_version:
        print(el)
