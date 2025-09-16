import telebot
import requests
import time
import threading
from datetime import datetime  # ✅ FIXED

BOT_TOKEN = "8268265905:AAFtJyfZ3hz9GYW82i0ScAiHC95fzhImX-M"
ALLOWED_GROUP_ID = -1002929955319
like_request_tracker = {}

VIP_USERS = {7306058394}

bot = telebot.TeleBot(BOT_TOKEN)

def call_api(region, uid):
    url = f"https://gagan-like-api-seven.vercel.app/like?uid={uid}&server_name={region}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200 or not response.text.strip():
            return "API_ERROR"
        return response.json()
    except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
        return "API_ERROR"

def process_like(message, region, uid):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in VIP_USERS and like_request_tracker.get(user_id, False):
        bot.reply_to(message, "⚠️ You have exceeded your daily request limit! ⏳ Try again later.")
        return

    processing_msg = bot.reply_to(message, "⏳ Processing your request... 🔄")

    for text in ["🔄 Fetching data from server... 10%", 
                 "🔄 Validating UID & Region... 30%", 
                 "🔄 Sending like request... 60%", 
                 "🔄 Almost Done... 90%"]:
        time.sleep(1)
        bot.edit_message_text(text, chat_id, processing_msg.message_id)

    response = call_api(region, uid)

    if response == "API_ERROR":
        bot.edit_message_text("🚨 API ERROR! ⚒️ We are fixing it, please wait for 8 hours. ⏳", chat_id, processing_msg.message_id)
        return

    if response.get("status") == 1:
        if user_id not in VIP_USERS:
            like_request_tracker[user_id] = True  # Mark usage

        try:
            photos = bot.get_user_profile_photos(user_id)
            if photos.total_count > 0:
                file_id = photos.photos[0][-1].file_id
                bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    media=telebot.types.InputMediaPhoto(
                        file_id,
                        caption=f"✅ **Like Added Successfully!**\n"
                                f"🔹 **UID:** `{response.get('UID', 'N/A')}`\n"
                                f"🔸 **Player Nickname:** `{response.get('PlayerNickname', 'N/A')}`\n"
                                f"🔸 **Likes Before:** `{response.get('LikesbeforeCommand', 'N/A')}`\n"
                                f"🔸 **Likes After:** `{response.get('LikesafterCommand', 'N/A')}`\n"
                                f"🔸 **Likes By Bot:** `{response.get('LikesGivenByAPI', 'N/A')}`\n\n"
                                "🗿 **SHARE US FOR MORE:**\n https://youtube.com/@teamxcutehack",
                        parse_mode="Markdown"
                    )
                )
                return
        except:
            pass

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=processing_msg.message_id,
            text=f"✅ **Like Added Successfully!**\n"
                 f"🔹 **UID:** `{response.get('UID', 'N/A')}`\n"
                 f"🔸 **Player Nickname:** `{response.get('PlayerNickname', 'N/A')}`\n"
                 f"🔸 **Likes Before:** `{response.get('LikesbeforeCommand', 'N/A')}`\n"
                 f"🔸 **Likes After:** `{response.get('LikesafterCommand', 'N/A')}`\n"
                 f"🔸 **Likes By Bot:** `{response.get('LikesGivenByAPI', 'N/A')}`\n\n"
                 "🗿 **SHARE US FOR MORE:**\n https://youtube.com/@teamxcutehack",
            parse_mode="Markdown"
        )
    else:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=processing_msg.message_id,
            text=f"💔 UID `{uid}` has already received Max Likes for Today 💔.\n"
                 "🔄 Please Try a different UID.",
            parse_mode="Markdown"
        )

@bot.message_handler(commands=['like'])
def handle_like(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id != ALLOWED_GROUP_ID:
        bot.reply_to(message, "🚫 This group is not allowed to use this bot! ❌")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "❌ Incorrect format! Use: `/like {region} {uid}`\n📌 Example: `/like ind 8385763215`", parse_mode="Markdown")
        return

    region, uid = args[1], args[2]

    if not region.isalpha() or not uid.isdigit():
        bot.reply_to(message, "⚠️ Invalid input! Region should be text and UID should be numbers.\n📌 Example: `/like ind 8385763215`")
        return

    threading.Thread(target=process_like, args=(message, region, uid)).start()

# ✅ FIX: Functions moved OUTSIDE of handle_like (proper indentation)
def format_number(num):
    try:
        return f"{int(num):,}"
    except:
        return 'N/A'

def format_timestamp(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%d-%m-%Y %I:%M %p')
    except:
        return 'N/A'

def get_rank_from_points(points):
    points = int(points) if points else 0
    if points >= 6000: return 'Master'
    elif points >= 3125: return 'Heroic'
    elif points >= 2825: return 'Diamond III'
    elif points >= 2675: return 'Diamond II'
    elif points >= 2538: return 'Diamond I'
    elif points >= 2413: return 'Platinum IV'
    elif points >= 2288: return 'Platinum III'
    elif points >= 2163: return 'Platinum II'
    elif points >= 2038: return 'Platinum I'
    elif points >= 1913: return 'Gold IV'
    elif points >= 1788: return 'Gold III'
    elif points >= 1663: return 'Gold II'
    elif points >= 1550: return 'Gold I'
    elif points >= 1450: return 'Silver III'
    elif points >= 1350: return 'Silver II'
    elif points >= 1250: return 'Silver I'
    elif points >= 1150: return 'Bronze III'
    elif points >= 1050: return 'Bronze II'
    elif points >= 1000: return 'Bronze I'
    else: return 'Unranked'

def get_rank_show(showType):
    if showType == "CSR": return "Clash Squad Ranked"
    if showType == "BRR": return "Battle Royal Ranked"
    return "N/A"

@bot.message_handler(commands=['get'])
def handle_get(message):
    try:
        uid = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        return bot.reply_to(message, "❌ Please provide UID. Example:\n`/get 123456789`", parse_mode='Markdown')

    sent_msg = bot.reply_to(message, "🔍 Fetching player info, please wait...")

    try:
        res = requests.get(f'https://syncinfo.vercel.app/info?uid={uid}')
        if not res.ok:
            return bot.edit_message_text("❌ Failed to fetch player info.", message.chat.id, sent_msg.message_id)

        data = res.json()
        player = data.get('playerData', {})
        profile = data.get('profileInfo', {})
        guild = data.get('guildInfo', {})
        owner = data.get('guildOwnerInfo', {})
        pet = data.get('petInfo', {})
        social = data.get('socialInfo', {})
        credit = data.get('creditScoreInfo', {})
        developer = data.get('developerInfo', {})

        br_rank = get_rank_from_points(player.get('rankingPoints'))
        show = get_rank_show(social.get('rankShow'))

        msg = f"👤 *ACCOUNT BASIC INFO*\n"
        msg += f"├ Name: `{player.get('nickname', 'N/A')}`\n"
        msg += f"├ UID: `{player.get('accountId', 'N/A')}`\n"
        msg += f"├ Level: `{player.get('level', 'N/A')} ({format_number(player.get('exp'))})`\n"
        msg += f"├ Prime Level: `{player.get('primeLevel', {}).get('primeLevel', 'N/A')}`\n"
        msg += f"├ Region: `{player.get('region', 'N/A')}`\n"
        msg += f"├ Likes: `{format_number(player.get('liked'))}`\n"
        msg += f"├ Gender: `{social.get('gender', 'N/A')}`\n"
        msg += f"├ Language: `{social.get('language', 'N/A')}`\n"
        msg += f"└ Signature: `{social.get('signature', 'N/A')}`\n\n"

        msg += f"🎮 *ACCOUNT ACTIVITY*\n"
        msg += f"├ OB Version: `{player.get('releaseVersion', 'N/A')}`\n"
        msg += f"├ Badges: `{player.get('badgeCnt', 'N/A')}`\n"
        msg += f"├ BR Rank: `{br_rank}` ({format_number(player.get('rankingPoints'))})\n"
        msg += f"├ CS Points: `{format_number(player.get('csRankingPoints'))}`\n"
        msg += f"├ Mode Prefer: `{social.get('modePrefer', 'N/A')}`\n"
        msg += f"├ Show Rank Mode: `{show}`\n"
        msg += f"├ Active Time: `{social.get('timeActive', 'N/A')}`\n"
        msg += f"├ Online Time: `{social.get('timeOnline', 'N/A')}`\n"
        msg += f"├ Honor Score: `{credit.get('creditScore', 'N/A')}`\n"
        msg += f"├ Score Period Ends: `{format_timestamp(credit.get('periodicSummaryEndTime'))}`\n"
        msg += f"├ Created At: `{format_timestamp(player.get('createAt'))}`\n"
        msg += f"└ Last Login: `{format_timestamp(player.get('lastLoginAt'))}`\n\n"

        msg += f"👕 *ACCOUNT LOOKS*\n"
        msg += f"├ Avatar ID: `{profile.get('avatarId', 'N/A')}`\n"
        msg += f"├ Banner ID: `{player.get('bannerId', 'N/A')}`\n"
        msg += f"├ HeadPic: `{player.get('headPic', 'N/A')}`\n"
        msg += f"├ Weapon Skins: `{player.get('weaponSkinShows', 'N/A')}`\n"
        msg += f"├ Equipped Items: `{', '.join(profile.get('equippedItems') or [])}`\n"
        msg += f"└ Skills: `{', '.join(profile.get('EquippedSkills') or [])}`\n\n"

        if pet:
            msg += f"🐾 *PET INFO*\n"
            msg += f"├ Pet Name: `{pet.get('name', 'N/A')}`\n"
            msg += f"├ Level: `{pet.get('level', 'N/A')}`\n"
            msg += f"├ Exp: `{format_number(pet.get('exp'))}`\n"
            msg += f"├ Selected Skill: `{pet.get('selectedSkillId', 'N/A')}`\n"
            msg += f"└ Marked Star: `{pet.get('isMarkedStar', False)}`\n\n"

        if guild:
            msg += f"🛡️ *GUILD INFO*\n"
            msg += f"├ Name: `{guild.get('clanName', 'N/A')}`\n"
            msg += f"├ ID: `{guild.get('clanId', 'N/A')}`\n"
            msg += f"├ Level: `{guild.get('clanLevel', 'N/A')}`\n"
            msg += f"├ Members: `{guild.get('memberNum', 'N/A')}` / `{guild.get('capacity', 'N/A')}`\n"
            if owner:
                msg += f"└ Leader: `{owner.get('nickname', 'N/A')} ({owner.get('accountId', 'N/A')})`\n"

        if developer:
            msg += f"\n👨‍💻 *DEVELOPER INFO*\n"
            msg += f"├ Name: `{developer.get('developerName', 'N/A')}`\n"
            msg += f"├ Github: {developer.get('github', 'N/A')}\n"
            msg += f"├ YouTube: {developer.get('youtube', 'N/A')}\n"
            msg += f"└ Signature: `{developer.get('signature', 'N/A')}`\n"

        bot.edit_message_text(msg, chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

    except Exception as e:
        print("Error:", e)
        bot.edit_message_text(f"❌ Error occurred:\n`{str(e)}`", message.chat.id, sent_msg.message_id, parse_mode='Markdown')

print("🤖 Bot is running...")
bot.polling(none_stop=True)