class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7576729648"
    sudo_users = ["7576729648", "7692444709"]
    GROUP_ID = -1002691911300
    TOKEN = "8106403386:AAHGLVa7QWJ1akWpZ7mV6hMRQ1ULH2GvkiM"
    mongo_url = "mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = [
        "https://telegra.ph/file/b925c3985f0f325e62e17.jpg",
        "https://telegra.ph/file/4211fb191383d895dab9d.jpg"
    ]

    SUPPORT_CHAT = "NARUTO_X_SUPPORT"
    UPDATE_CHAT = "NARUTO_X_SUPPORT"
    BOT_USERNAME = "BlackXdevilbot"
    CHARA_CHANNEL_ID = "-1002527530412"

    api_id = 26626068
    api_hash = "bf423698bcbe33cfd58b11c78c42caa2"

class Production(Config):
    LOGGER = True

class Development(Config):
    LOGGER = True