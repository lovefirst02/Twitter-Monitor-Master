import tweepy
import asyncio
import time
import re
import datetime
from threading import Thread
import threading
from discord_webhook import DiscordEmbed, DiscordWebhook
import random
import discord
from discord.ext import commands
import os
import ctypes
import inspect
import json
import _thread
import random
import execjs
import requests
import webbrowser


#------------------------------------無 用 -------------------------------------
# async def read_from_txt():
#     raw_lines = []
#     lines = []
#     try:
#         f = open('handle.txt', 'r')
#         raw_lines = f.readlines()
#         f.close()
#     except:
#         raise FileNotFound()
#
#     if(len(raw_lines) == 0):
#         raise NoDataLoaded()
#
#     for line in raw_lines:
#         lines.append(line.strip("\n"))
#
#     return lines
#
# loop = asyncio.get_event_loop()

#----------------------------------- 字符畫--------------------------------------
draw = open('string.txt')
print(draw.read())

#----------------------------------定義 部分------------------------------------

# keywords = list(map(str, input("輸入關鍵字 (必須填,如:cyber amnotify): ").split()))

blacklist = ['twitter','t.co']
webhookurl = 'webhook url here'

bot = commands.Bot(command_prefix = '!') #DiscordBot定義指令
api_list = []
api_private_list = []
threadlist = []
checkaco = []
api_start_list = []
headers = {
   'Host': "app.poizon.com",
   'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
   " Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.4.501 NetType/WIFI "
   "MiniProgramEnv/Windows WindowsWechat",
   'appid': "wxapp",
   'appversion': "4.4.0",
   'content-type': "application/x-www-form-urlencoded",
   'Accept-Encoding': "gzip, deflate",
   'Accept': "*/*",
}
oldtweet = ''

#--------------------------------讀取json並打包---------------------------------
jsonfile = open('config.json','r')
file = json.load(jsonfile)
for item in file:
    consumer_key = item['a']
    consumer_secret = item['b']
    access_token = item['c']
    access_token_secret = item['d']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
    api_list.append(api)
    api_private_list.append(api)

#-------------------------------關閉Thread 部分---------------------------------
async def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

async def stop_thread(thread):
    await _async_raise(thread.ident, SystemExit)

#---------------------------------Monitor 部分----------------------------------
def browser_open(urls):
    for url in urls:
        if all(x not in url.lower() for x in blacklist):
            webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(url)
            print(f'GO!!打開 {url}')

def get_first(handle):
    now = datetime.datetime.now()
    try:
        first = api.user_timeline(screen_name = handle, count = 1,include_entities=True, tweet_mode = 'extended')
        tweet = [[tweet.full_text] for tweet in first]
    except tweepy.RateLimitError:
        print("Get Limit Error")
        print('sleep time')
        time.sleep(900)

    print(str(now) + ' ----------- ' + 'Get {} First Comlete'.format(handle))

def webhook(handle,new):
    global ub,mb,meb,new_description
    ub = False
    mb = False
    meb = False
    old_url = []
    new_url = []
    new_description = ''
    description = new.full_text
    print(description)
    id_str = new.id_str
    quick = '[**Profile**](https://twitter.com/{})'.format(handle) + ' - ' + '[**Tweet**](https://twitter.com/{}/status/{})'.format(handle,id_str) + '\n'
    try:
        s = ''
        urlf = new.entities['urls']
        for i in urlf:
            tur = i['url']
            uri = i['expanded_url']
            s += '[**t.co**]({})'.format(tur) + ' - ' + uri + "\n"
            old_url.append(tur)
            new_url.append(uri)
        if len(old_url) > 0:
            d = dict(zip(old_url, new_url))
            p = r'\b('+'|'.join(old_url) + r')\b'
            new_description = re.sub(p, lambda m: d.get(m.group()),description)
            ub = True
    except:
        ub = False
    #find media
    try:
        media = ''
        i = 0
        medialen = new.extended_entities.get('media',[])
        while (len(medialen) > i):
            media += new.entities['media'][i]['media_url']
            print(media)
            i=i+1
    except:
            meb = False
    #傳送WEBHOOK
    webhook = DiscordWebhook(url=webhookurl)
    if ub == True:
        embed = DiscordEmbed(title=handle,description ='**Text:**' + '\n' + new_description + '\n\n' + '**Quick:**'+ '\n' + quick + '\n' + '**Url:**' + '\n' + s ,color=random.randint(0, 16777215))
    else:
        embed = DiscordEmbed(title=handle,description ='**Text:**\n' + description + '\n\n' + '**Quick:**\n' + quick,color=random.randint(0, 16777215))
    #if ub == True:
        #embed.add_embed_field(name='**tweet**',value=new_description,inline=False)
    #else:
        #embed.add_embed_field(name='**tweet**',value=description,inline=False)
    #embed.add_embed_field(name='**Quick：**', value='[**Profile**](https://twitter.com/{})'.format(handle) + ' - ' + '[**Tweet**](https://twitter.com/{}/status/{})'.format(handle,id_str), inline=False)
    #if s:
        #embed.add_embed_field(name='**Url**',value=s,inline=False)
    if media:
        embed.set_image(url=media)
    webhook.add_embed(embed)
    webhook.execute()

    #判斷是否有MentionUser
    try:
        mentions = new.entities['user_mentions']
        men_user = [men_user['screen_name'] for men_user in mentions]
        for mention_user in men_user:
            mentiontext = api.user_timeline(screen_name = mention_user, count=1,include_entities=True, tweet_mode='extended')[0]
            mentionuser = api.get_user(screen_name = mention_user)
            mention_full = mentiontext.full_text
            mentionicon = mentionuser.profile_image_url
            #mention_full2 = [[mentiontext.full_text] for mention_full2 in mentiontext]
            mb = True
            mention_webhook = DiscordWebhook(url=webhookurl)
            mention_embed = DiscordEmbed(title='***Mention User***', color=0xffe006)
            mention_embed.set_author(name='Tweet From ' + mention_user, icon_url=mentionicon)
            mention_embed.add_embed_field(name='***tweet***', value=mention_full, inline=False)
            mention_webhook.add_embed(mention_embed)
            mention_webhook.execute()
    except:
            mb = False

    try:
        if re.search('\S\S\S\S\S-\S\S\S\S\S', str(description)):
            tkey = ''
            tkf = re.findall(r'(\S\S\S\S\S-\S\S\S\S\S-\S\S\S\S\S-\S\S\S\S\S-\S\S\S\S\S)',str(description))
            for t in tkf:
                tkey += 'https://resellaio.com/activate/{}'.format(t) + '\n'
            keyhook = DiscordWebhook(url=webhookurl)
            keyembed = DiscordEmbed(title='URL WITH KEY',description ='**Key Link:**' + '\n' + tkey,color=random.randint(0, 16777215))
            keyhook.add_embed(keyembed)
            keyhook.execute()
    except Exception as e:
        print(e)

def monitor(handle,sleeptime):
    old = get_first(handle)
    #old_retweet = get_retweet(handle)
    while True:
        for api in api_list:
            try:
                now = datetime.datetime.now()
                new = api.user_timeline(screen_name = handle, count=1,include_entities=True, tweet_mode='extended')[0]
                #newtext = new.full_text
                #id_str = new.id_str
                print( str(now) + ' --------- ' + str(api) + ' ----------- ' + 'Get {} New Comlete'.format(str(handle)))
                if old != new:
                    #判斷是否為RETWEET
                    if ('RT @' in str(new)):
                        print('這是個RT')
                    else:
                        webhook(handle,new)
                old = new
                time.sleep(float(sleeptime))
            except Exception as e:
                print(e)
            except tweepy.TweepError as e:
                print(e)
            except IndexError as e:
                print(e)
            except ValueError as e:
                print(e)

def sync_monitor(api,handle,sleeptime):
    old = api.user_timeline(screen_name = handle, count=1,include_entities=True, tweet_mode='extended')[0]
    #old_retweet = get_retweet(handle)
    while True:
        try:
            now = datetime.datetime.now()
            new = api.user_timeline(screen_name = handle, count=1,include_entities=True, tweet_mode='extended')[0]
            #newtext = new.full_text
            #id_str = new.id_str
            print( str(now) + ' --------- ' + str(api) + ' ----------- ' + 'Get {} New Comlete'.format(str(handle)))
            if old != new:
                #判斷是否為RETWEET
                if ('RT @' in str(new)):
                    print('這是個RT')
                else:
                    webhook(handle,new)
                    old = new
            time.sleep(float(sleeptime))
        except Exception as e:
            print(e)
        except tweepy.TweepError as e:
            print(e)
        except IndexError as e:
            print(e)
        except ValueError as e:
            print(e)

def continue_monitor(handle,sleeptime):
    continue_list = []
    tweet_list = []
    jsonfile = open('config2.json','r')
    file = json.load(jsonfile)
    for item in file:
        consumer_key = item['a']
        consumer_secret = item['b']
        access_token = item['c']
        access_token_secret = item['d']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        continue_list.append(api)

    api = random.choice(continue_list)
    try:
        old = api.user_timeline(screen_name = handle, count=1,include_entities=True, tweet_mode='extended')[0]
        tweet_list.append(old.full_text)
        print('Get Old Complete ------ {}'.format(api))
    except tweepy.RateLimitError:
        api = random.choice(continue_list)
        print('Get Old Limit 轉換 API ------ {}'.format(api))
    while True:
        try:
            now = datetime.datetime.now()
            new = api.user_timeline(screen_name = handle, count=1,include_entities=True, tweet_mode='extended')[0]
            # continue_list.append(new)
            print( str(now) + ' --------- ' + str(api) + ' ----------- ' + 'Get {} New Comlete'.format(str(handle)))
            # for twe in tweet_list:
            if new.full_text not in tweet_list :
                urls = re.findall("(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+", str(new.full_text))

                #判斷是否為RETWEET
                if ('RT @' in str(new)):
                    print('這是個RT')
                elif(urls):
                    browser_open(urls)

                webhook(handle,new)
                tweet_list.append(new.full_text)
            time.sleep(float(sleeptime))
        except tweepy.RateLimitError:
            api = random.choice(continue_list)
            print('Get Limit 轉換 API ------ {}'.format(api))
        except Exception as e:
            print(e)
        except tweepy.TweepError as e:
            print(e)
        except IndexError as e:
            print(e)
        except ValueError as e:
            print(e)

async def continue_monitorv2(handle):
    count = 0
    continue_list = []
    jsonfile = open('config2.json','r')
    file = json.load(jsonfile)
    for item in file:
        consumer_key = item['a']
        consumer_secret = item['b']
        access_token = item['c']
        access_token_secret = item['d']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        continue_list.append(api)

    api = random.choice(continue_list)
    oldtweet = api.user_timeline(screen_name = handle, count=1,include_entities=True, tweet_mode='extended')[0]
    try:
        now = datetime.datetime.now()
        new = api.user_timeline(screen_name = handle, count=1,include_entities=True, tweet_mode='extended')[0]
        print( str(now) + ' --------- ' + str(api) + ' ----------- ' + 'Get {} New Comlete'.format(str(handle)))
        if oldtweet != new:
            #判斷是否為RETWEET
            if ('RT @' in str(new)):
                print('這是個RT')
            else:
                webhook(handle,new)
                oldtweet = new

    except tweepy.RateLimitError:
        api = random.choice(continue_list)
        print('Get Limit 轉換 API ------ {}'.format(api))
    except Exception as e:
        print(e)
    except tweepy.TweepError as e:
        print(e)
    except IndexError as e:
        print(e)
    except ValueError as e:
        print(e)

async def start_v2(handle,sleeptime):
    while True:
        await continue_monitorv2(handle)
        time.sleep(float(sleeptime))

async def follow_fun(handle):
    for api in api_list:
        friends = api.friends()
        if handle not in friends:
            api.create_friendship(handle)
            print('sucess')
        else:
            print('已經追隨')

async def destroy_fun(handle):
    for api in api_list:
        try:
            api.destroy_friendship(handle)
            print('sucess')
        except Exception as e:
            print(e)

#---------------------------------Thread 部分-----------------------------------
#無用
async def main(handle,sleeptime):
    tasks = []
    task = asyncio.create_task(monitor(handle,sleeptime))
    tasks.append(task)
    loop = asyncio.get_event_loop()
    hey = loop.run_until_complete(asyncio.gather(*tasks))
    return hey

#thread with monitor部分
async def thread(handle,sleeptime):
    tsk = []
    t = Thread(target=monitor,args=[handle,sleeptime])
    t.setName(handle)
    threadlist.append(t)
    t.start()
    return t

#單獨開啟各個API的Thread
async def api_thread(api,handle,sleeptime):
    try:
        t = Thread(target=sync_monitor,args=[api,handle,sleeptime])
        t.setName(handle)
        threadlist.append(t)
        t.start()
    except Exception as e:
        print('錯誤:{}'.format(e))

#thread with sync-monitor部分
async def thread_multi(handle,sleeptime):
    tsk = []
    t = Thread(target=sync_monitor,args=[api_list[0],handle,sleeptime])
    t2 = Thread(target=sync_monitor,args=[api_list[1],handle,sleeptime])
    t.setName(handle)
    t2.setName(handle)
    t.start()
    t2.start()
    threadlist.append(t)
    threadlist.append(t2)
    return t,t2

#thread with continue_monitor部分
async def continue_thread(handle,sleeptime):
    tsk = []
    t = Thread(target=continue_monitor,args=[handle,sleeptime])
    t.setName(handle)
    threadlist.append(t)
    t.start()
    return t

#-------------------------------DU API 部分-------------------------------------
async def get_search_by_keywords_url(sku):
    with open('dusign.js', 'r', encoding='utf-8')as f:
        all_ = f.read()
        ctx = execjs.compile(all_)
        # 53489
        sign = ctx.call('getSign',
                        'limit20page0sortMode1sortType0title{}unionId19bc545a393a25177083d4a748807cc0'.format(sku))
        search_by_keywords_url = 'https://app.poizon.com/api/v1/h5/product/fire/search/list?title={}&page=0&sortType=0&sortMode=1&' \
                                 'limit=20&unionId=&sign={}'.format(sku, sign)

        return search_by_keywords_url #調用毒APP搜索接口

async def product_id(sku):
    productid = []
    search_by_keywords_url = await get_search_by_keywords_url(sku)
    search_by_keywords_response =  requests.get(url=search_by_keywords_url, headers=headers)
    t = json.loads(search_by_keywords_response.text)
    searchlist = t['data']['productList']
    for i in searchlist:
        id = i['productId']
        productid.append(id)
    return productid #獲取產品ID

async def get_product(sku):
    url = []
    id = await product_id(sku)
    for productId in id:
        with open('dusign.js','r',encoding='utf-8') as f:
            all_ = f.read()
            ctx = execjs.compile(all_)
            sign = ctx.call('getSign','productId{}productSourceNamewx19bc545a393a25177083d4a748807cc0'.format(productId))
            product_detail_url = 'https://app.poizon.com/api/v1/h5/index/fire/flow/product/detail?' \
            'productId={}&productSourceName=wx&sign={}'.format(productId, sign)
            url.append(product_detail_url)
    return url#調用毒APP商品詳情接口

async def main(sku):
    url = await get_product(sku)
    text = ''
    for product_detail_url in url:
        product_detail_response = requests.get(url=product_detail_url, headers=headers)
        j = json.loads(product_detail_response.text)
        item = j['data']['sizeList']
        title = j['data']['detail']['title']
        image = j['data']['detail']['logoUrl']
        jsonsku = j['data']['detail']['articleNumber']
        authprice = j['data']['detail']['authPrice']
        retail = str(authprice).rstrip("00")
        if sku == jsonsku:
            for i in item:
                size = i['size']
                price = i['item']['price']
                pricefix = str(price).rstrip("00")
                text += '{} : {}'.format(size,pricefix) + '\n'

            webhook = DiscordWebhook(url = webhookurl)
            embed = DiscordEmbed(title = title,color = random.randint(0, 16777215))
            embed.set_thumbnail(url = image)
            embed.add_embed_field(name = '型號:',value = sku, inline = True)
            embed.add_embed_field(name = '發售價:',value = retail, inline = True)
            embed.add_embed_field(name = '尺寸&價格:',value = text,inline = False)
            embed.set_footer(text = 'By Cody_W#8711')
            webhook.add_embed(embed)
            webhook.execute() #main function

#-------------------------------DISCORD BOT 部分--------------------------------
@bot.event
async def on_ready():
    bot_name = bot.user.name
    login_text = '歡迎使用Twitter-Monitor,BOT名稱為：{}'.format(bot_name)
    print('-------------------{}------------------'.format(login_text))

#無用
@bot.command()
async def ioi(ctx,arg,sleeptime):
    try:
        await ctx.send('成功加入**{}**到Monitor,Delay為**{}**'.format(arg,sleeptime))
        await main(arg,sleeptime)
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

#對應THREAD
#所有API監控同一個HANDLE,且在同一個Thread !add (handle) (sleeptime)
@bot.command()
async def add(ctx,arg,sleeptime):
    atext = ''
    checkaco.append(arg)
    try:
        await ctx.send('成功加入**{}**到Monitor,Delay為：**{}**'.format(arg,sleeptime))
        await thread(arg,sleeptime)
        for a in checkaco:
            atext += '**{}**正在被監視{}'.format(a,"\n")
        await ctx.send(atext)
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

#對應THREAD_MULTI
#所有API監控同一個HANDLE,且在不同的Thread !start (handle) (sleeptime)
@bot.command()
async def start(ctx,arg,sleeptime):
    atext = ''
    checkaco.append(arg)
    try:
        await ctx.send('成功加入**{}**到Monitor,Delay為：**{}**'.format(arg,sleeptime))
        await thread_multi(arg,sleeptime)
        for a in checkaco:
            atext += '**{}**正在被監視{}'.format(a,"\n")
        await ctx.send(atext)
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

#對應API_THREAD
#獨立API監控不同的HANDLE,且在不同的Thread !apistart (api) (handle) (sleeptime)
@bot.command()
async def apistart(ctx,apicount,arg,sleeptime):
    api_start_list = api_list
    try:
        await ctx.send('成功加入**{}**到Monitor,Delay為：**{}**,API為：**||{}||**'.format(arg,sleeptime,api_start_list[int(apicount)]))
        await api_thread(api_start_list[int(apicount)],arg,sleeptime)
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

#對應CONTINUE_THREAD
#獨立API監控HANDLE,遇到Rate Limit轉換API,於同一個Thread !constart (handle) (sleeptime)
@bot.command()
async def constart(ctx,arg,sleeptime):
    atext = ''
    checkaco.append(arg)
    try:
        await ctx.send('成功加入**{}**到Monitor,Delay為：**{}**'.format(arg,sleeptime))
        await continue_thread(arg,sleeptime)
        for a in checkaco:
            atext += '**{}**正在被監視{}'.format(a,"\n")
        await ctx.send(atext)
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

@bot.command()
async def constartv2(ctx,arg,sleeptime):
    try:
        await start_v2(arg,sleeptime)
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

#停止所有運行中的Thread
@bot.command()
async def stop(ctx):
    ctext = ''
    await ctx.send('**{}**個Thread即將被關閉'.format(len(threadlist)))
    for i in threadlist:
        try:
            await ctx.send('**||{}||** ---- **stop**'.format(i))
            await stop_thread(i)
        except Exception as e:
            await ctx.send('錯誤:{}'.format(e))
    del checkaco[:]
    del threadlist[:]
    if len(checkaco) == 0:
        await ctx.send('No Account In Monitor')
    else:
        try:
            for a in checkaco:
                ctext += f'{a}\n'
            await ctx.send(ctext)
        except Exception as e:
            await ctx.send('錯誤:{}'.format(e))

#查看所有運行中的Thread
@bot.command()
async def view(ctx):
    viewtext = ''
    count = 0
    if len(threadlist) == 0:
        await ctx.send('**0**個Thread運行中')
    else:
        for i in threadlist:
            viewtext += '**{}** . **||{}||** ----- **正在運行中**'.format(count,i) + '\n'
            count = count + 1
        await ctx.send(viewtext)

#查看有多少API在MONITOR中
@bot.command()
async def apiview(ctx):
    count = 0
    viewtext = ''
    i = len(api_list)
    for a in api_list:
        viewtext += '**{}** . **||{}||**'.format(count,a) + '\n'
        count = count + 1
    await ctx.send('目前總共有**{}**個API在**API_LIST**'.format(i) + '\n' + viewtext)

#Follow with handle 如果推特沒有FOLLOW,!follow (handle)
@bot.command()
async def follow(ctx,arg):
    try:
        await follow_fun(arg)
        await ctx.send('**Follow** @{} 成功'.format(arg))
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

#UNFollow with handle UNFOLLOW想退追隨的Handle,!follow (handle)
@bot.command()
async def unfollow(ctx,arg):
    try:
        await destroy_fun(arg)
        await ctx.send('**UnFollow** @{} 成功'.format(arg))
    except Exception as e:
        await ctx.send('錯誤:{}'.format(e))

@bot.command()
async def du(ctx,sku):
    await main(sku) #輸入指令!check (sku),就會調用 main function,並且send to webhook

#HELP指令編寫,!help
bot.remove_command('help')
@bot.command()
async def help(ctx):
    embed = discord.Embed(title = 'Twitter-Monitor 指令',color = random.randint(0, 16777215))
    embed.add_field(name = '!add (handle) (sleeptime)', value = '所有API監控同一個HANDLE,在同一個Thread', inline = False)
    embed.add_field(name = '!start (handle) (sleeptime)', value = '所有API監控同一個HANDLE,在不同的Thread', inline = False)
    embed.add_field(name = '!apistart (api) (handle) (sleeptime)', value = '獨立API監控不同的HANDLE,在不同的Thread', inline = False)
    embed.add_field(name = '!constart (handle) (sleeptime)', value = '獨立API監控HANDLE,遇到Rate Limit轉換API', inline = False)
    embed.add_field(name = '!follow (handle)', value = 'Follow想Follow的Handle', inline = False)
    embed.add_field(name = '!unfollow (handle)', value = 'unFollow想unFollow的Handle', inline = False)
    embed.add_field(name = '!stop', value = '停止所有運行中的Thread', inline = False)
    embed.add_field(name = '!view', value = '查看所有運行中的Thread', inline = False)
    embed.add_field(name = '!apiview', value = '查看API的擁有數', inline = False)
    embed.add_field(name = '!du (sku)', value = '可以查毒的價格', inline = False)
    await ctx.send(embed=embed)

bot.run('token here') #DiscordBot運行
