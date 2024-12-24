"""``pytest`` configuration."""

import pytest

#from echopype.testing import TEST_DATA_FOLDER

import os
import pooch
from pathlib import Path
from zipfile import ZipFile


ECHOPYPE_RESOURCES = pooch.create(
    path=pooch.os_cache("echopype"),
    base_url="https://github.com/oftfrfbf/echopype-test-data/releases/download/{version}/",
    version='2024.12.21',
    retry_if_failed=1,
    registry={
        "ad2cp.zip": "sha256:8c0e45451eca31b478e7ba9d265fc1bb5257045d30dc50fc5299d2df2abe8430",
        "azfp.zip": "sha256:6b2067e18e71e7752b768cb84284fef3e0d82b5b775ea2499d52df8202936415",
        "azfp6.zip": "sha256:b13ad0cb026d42bd0112d2999e5f63ba28226e4c79ffe335d650fe3f28db760d",
        "ea640.zip": "sha256:10bcd57c9d382e680e26a0f78b3e1c8bda8c68799d69334ab63031c10650d114",
        "ecs.zip": "sha256:e873754f40ec7142c5ece9706a9c63e6f49666b534c79aeac54952ece8267439",
        #"ek60.zip": "sha256:2334ba26f00720c1d29241d35f32c9cddce3fdd1d3dd2b1a99d8962f04e977ee",
        "ek60_missing_channel_power.zip": "sha256:82a9f89c848f6925f779ef6b8d47e6fb1c59e720a303830010f73e45e82c6609",
        "ek80.zip": "sha256:e46dea3ba4531d2576bbae2cd17a33ead48cb594244dd611fddd98e53901aa39",
        "ek80_bb_complex_multiplex.zip": "sha256:4eac7b0f40bdd8405aac38e114b47cc1901f7614002e7a5ea9a642bbcb884f93",
        "ek80_bb_with_calibration.zip": "sha256:362613ecce383136be16e0a7d7c74a33ef11866d5a0b6bf1581172b27186790a",
        "ek80_duplicate_ping_times.zip": "sha256:f2affc25c0972c23ef2f9e1e78a7627bffe6105d39e5b4e9c68b3e8bb81e08b5",
        "ek80_ext.zip": "sha256:dbaf35f2af1526e4d5a9e6b65b22e090d4db0e0355d8be8e5c2255fe03b65475",
        "ek80_invalid_env_datagrams.zip": "sha256:12f8bc32aecaf3c1c8a506491be2346382aed76f6c6dd8d60847f6915b597c50",
        "ek80_missing_sound_velocity_profile.zip": "sha256:56fd98974cf1dd1cd400358045cfbcf82c52e431e4acf822146458dbdf11a59e",
        "ek80_new.zip": "sha256:644ef2c2d89e52b63635eaf523eb0b0385580b1bacd189aa39c62db69943abb6",
        "es60.zip": "sha256:7abf0635a7d1365d075d9b4ce32abef86efe2ea1fda84be4f07187f384709ff5",
        "es70.zip": "sha256:e7d58335b0049b3709e08663913925d75a76250f787f84019dc5f3fadfc0983a",
        "es80.zip": "sha256:9547583dbd6ac77375384e614cd559ff61639d36f082f1ce80855f9b57a52213",
    },
)
ECHOPYPE_RESOURCE2 = pooch.create(
    path=pooch.os_cache("echopype"),
    base_url="https://github.com/oftfrfbf/echopype-test-data/releases/download/{version}/",
    version='2024.12.23',
    retry_if_failed=1,
    registry={
        "ek60.zip": "sha256:872e8c021dc8b2fe22b8ff62659c1737e80bddee5835429d20e51a7a71dd9ef8",
    },
)

def unpack(fname, action, pup):
    unzipped = Path(fname.split('.zip')[0]).parent # + ".unzipped"
    unzipped_child = fname.split('.zip')[0]
    if action in ("update", "download") or not os.path.exists(unzipped_child):
        with ZipFile(fname, "r") as zip_file:
            zip_file.extractall(path=unzipped)
    return unzipped

def fetch_zipped_file(file_path, resource=ECHOPYPE_RESOURCES):
    fname = resource.fetch(
        fname=file_path,
        processor=unpack,
        progressbar=True,
    )
    return Path(fname).joinpath(Path(file_path).stem)

ad2cp = fetch_zipped_file("ad2cp.zip")
azfp = fetch_zipped_file("azfp.zip")
azfp6 = fetch_zipped_file("azfp6.zip")
ea640 = fetch_zipped_file("ea640.zip")
ecs = fetch_zipped_file("ecs.zip")
#ek60 = fetch_zipped_file("ek60.zip")
ek60 = fetch_zipped_file("ek60.zip", ECHOPYPE_RESOURCE2)
ek60_missing_channel_power = fetch_zipped_file("ek60_missing_channel_power.zip")
ek80 = fetch_zipped_file("ek80.zip")
ek80_bb_complex_multiplex = fetch_zipped_file("ek80_bb_complex_multiplex.zip")
ek80_bb_with_calibration = fetch_zipped_file("ek80_bb_with_calibration.zip")
ek80_duplicate_ping_times = fetch_zipped_file("ek80_duplicate_ping_times.zip")
ek80_ext = fetch_zipped_file("ek80_ext.zip")
ek80_invalid_env_datagrams = fetch_zipped_file("ek80_invalid_env_datagrams.zip")
ek80_missing_sound_velocity_profile = fetch_zipped_file("ek80_missing_sound_velocity_profile.zip")
ek80_new = fetch_zipped_file("ek80_new.zip")
es60 = fetch_zipped_file("es60.zip")
es70 = fetch_zipped_file("es70.zip")
es80 = fetch_zipped_file("es80.zip")

@pytest.fixture(scope="session")
def dump_output_dir():
    return Path(ad2cp).parent / "dump"
    #return TEST_DATA_FOLDER / "dump"


@pytest.fixture(scope="session")
def test_path():
    return {
        #'ROOT': TEST_DATA_FOLDER, # This needs to point to parent
        'ROOT': Path(ad2cp).parent,

        'AD2CP': ad2cp,
        'AZFP': azfp,
        'AZFP6': azfp6,
        'EA640': ea640,
        'ECS': ecs,
        'EK60': ek60,
        'EK60_MISSING_CHANNEL_POWER': ek60_missing_channel_power,
        'EK80': ek80,
        ### Note: EK80_CAL points to ek80_bb_with_calibration ###
        'EK80_CAL': ek80_bb_with_calibration,
        'EK80_BB_COMPLEX_MULTIPLEX': ek80_bb_complex_multiplex,
        'EK80_BB_WITH_CALIBRATION': ek80_bb_with_calibration,
        'EK80_DUPLICATE_PING_TIMES': ek80_duplicate_ping_times,
        'EK80_EXT': ek80_ext,
        'EK80_INVALID_ENV_DATAGRAMS': ek80_invalid_env_datagrams,
        'EK80_MISSING_SOUND_VELOCITY_PROFILE': ek80_missing_sound_velocity_profile,
        'EK80_NEW': ek80_new,
        'ES60': es60,
        'ES70': es70,
        'ES80': es80,
    }


@pytest.fixture(scope="session")
def minio_bucket():
    return dict(
        client_kwargs=dict(endpoint_url="http://localhost:9000/"),
        key="minioadmin",
        secret="minioadmin",
    )
