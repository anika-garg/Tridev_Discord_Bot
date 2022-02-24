import discord
import os
import asyncio
from discord.ext import commands

# Custom modules
import db
import tfidf_summarizer

client = commands.Bot(command_prefix = '!')

# This takes a while and should be run only once on startup
mongo_client = db.connect_to_mongo(db.user, db.pswd)

# Get the keyword list for test server (each guild will have their own list)
# NOTE: This code must be updated to use with different guilds
users_collection = db.get_collection(
    db.get_db(mongo_client, db.db_name),
    db.collections[1]
)
message_collection = db.get_collection(
    db.get_db(mongo_client, db.db_name),
    db.collections[2]
)
all_messages_collection = db.get_collection(
    db.get_db(mongo_client, db.db_name),
    db.collections[3]
)
keywords_collection = db.get_collection(
    db.get_db(mongo_client, db.db_name),
    db.collections[0]
)

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command(name = 'about')
async def about(ctx):

    Embed = discord.Embed(
    title = "Kethan Bethamcharla", description = "I am 17 years old"
    )

    await ctx.message.channel.send(embed = Embed)
# use embed to send the newsletter (this is a good idea)

@client.command(name = 'quit')
@commands.has_permissions(administrator=True)
async def close(ctx):
    await client.close()
    print('Bot Closed')
    mongo_client.close()
    print('Mongo connection closed')


@client.command(name = 'createKeywordCategory', aliases = ['ckc', 'createKeyCat'])
async def about(ctx, newCategory, *, newKeyword):
    # Not sure why we need the timestamp. Younghoon said it was imortant
    db.create_keyword_category(
        keywords_collection,
        users_collection,
        str(ctx.author),
        newCategory,
        newKeyword,
        ctx.guild.id
    )

    keywords_list = db.get_keywords(keywords_collection, ctx.guild.id)

    if newKeyword in keywords_list:
        await ctx.author.send('New Keyword Category created successfully')
    else:
        await ctx.author.send('New Keyword Catgeory not created successfully')


@client.command(name = 'addKeyword', aliases = ['addKW', 'aKW', 'addkeyword', 'akw'])
async def about(ctx, existingCategory, *, newKeyword):
    db.add_keyword(keywords_collection, users_collection, str(ctx.author), existingCategory, newKeyword, ctx.guild.id)

    keywords_list = db.get_keywords(keywords_collection, ctx.guild.id)

    if newKeyword in keywords_list:
        await ctx.author.send('Keyword added successfully')
    else:
        await ctx.author.send('Keyword not added successfully')


@client.command(name = 'addKeywordFromCategory', aliases = ['addKWFC', 'aKWFC', 'akwfc'])
async def about(ctx, *, category):
    db.add_all_keywords_from_category_to_user_keywords_list(keywords_collection, users_collection, str(ctx.author), category, ctx.guild.id)

    await ctx.auhtor.send('Keywords added successfully')


@client.command(name = 'getCategory', aliases = ['getC', 'gC', 'gc'])
async def about(ctx):
    categories_list = db.get_existing_keyword_categories(keywords_collection, ctx.guild.id)

    await ctx.author.send(categories_list)
    await ctx.author.send('These are the keyword categories')


@client.command(name = 'getKeywordsCategory', aliases = ['getKC', 'gKC', 'gkc'])
async def about(ctx, *, category):
    keywords_in_category = db.get_existing_keywords_in_specific_category(keywords_collection, category, ctx.guild.id)

    await ctx.author.send(keywords_in_category)
    await ctx.author.send('These are the keywords in the ' + category + ' category')


@client.command(name = 'myKeywords', aliases = ['myKW', 'mykw', 'mkw'])
async def about(ctx):
    # Updates keyword list
    keywords_list = db.get_keywords_of_user(users_collection, str(ctx.author), ctx.guild.id)

    await ctx.author.send(keywords_list)
    await ctx.author.send('These are your keywords')


@client.command(name = 'newsletter', aliases = ['summary', 'nl', 's'])
async def about(ctx, *, channel):
    messages = db.get_all_messages(all_messages_collection, ctx.guild.id, channel)
    summary = tfidf_summarizer.run_summarization(messages)

    Embed = discord.Embed(
        title = ("Newsletter from the " + channel + " channel in the " + ctx.guild.name + " server"),
        description = "*The summary is sent in multiple paragraphs due to size constrictions when sending it all in one paragraph*"
    )

    if len(summary)<1024:
        Embed.add_field(name = 'Summary', value = summary, inline = False)
    else:
        list_summary = summary_split(summary, [])
        for i in range(len(list_summary)):
            para_number = i+1
            Embed.add_field(name = "Paragraph {}".format(para_number), value = list_summary[i], inline = False)

    await ctx.author.send(embed = Embed)


@client.command(name = 'newsletterDay', aliases = ['nld'])
async def about(ctx, channel, date):
    messages = db.get_all_messages_from_specific_day(all_messages_collection, ctx.guild.id, channel, date)
    summary = tfidf_summarizer.run_summarization(messages)

    Embed = discord.Embed(
        title = ("Newsletter from the " + channel + " channel in the " + ctx.guild.name + " server"),
        description = "*The summary is sent in multiple paragraphs due to size constrictions when sending it all in one paragraph*"
    )

    if len(summary)<1024:
        Embed.add_field(name = 'Summary', value = summary, inline = False)
    else:
        list_summary = summary_split(summary, [])
        for i in range(len(list_summary)):
            para_number = i+1
            Embed.add_field(name = "Paragraph {}".format(para_number), value = list_summary[i], inline = False)

    await ctx.author.send(embed = Embed)

@client.command(name = 'newsletterKeyword', aliases = ['nlkw', 'nkw'])
async def about(ctx, channel, *, keyword):
    messages = db.get_messages_with_keyword(message_collection, ctx.guild.id, channel, keyword)
    summary = tfidf_summarizer.run_summarization(messages)

    Embed = discord.Embed(
        title = ("Newsletter from the " + channel + " channel in the " + ctx.guild.name + " server"),
        description = "*The summary is sent in multiple paragraphs due to size constrictions when sending it all in one paragraph*"
    )

    if len(summary)<1024:
        Embed.add_field(name = 'Summary', value = summary, inline = False)
    else:
        list_summary = summary_split(summary, [])
        for i in range(len(list_summary)):
            para_number = i+1
            Embed.add_field(name = "Paragraph {}".format(para_number), value = list_summary[i], inline = False)

    await ctx.author.send(embed = Embed)


@client.command(name = 'newsletterKeywordDay', aliases = ['nlkwd', 'nkwd'])
async def about(ctx, channel, date, *, keyword):

    messages = db.get_messages_with_keyword_specific_day(message_collection, ctx.guild.id, channel, keyword, date)
    summary = tfidf_summarizer.run_summarization(messages)

    Embed = discord.Embed(
        title = ("Newsletter from the " + channel + " channel in the " + ctx.guild.name + " server"),
        description = "*The summary is sent in multiple paragraphs due to size constrictions when sending it all in one paragraph*"
    )

    if len(summary)<1024:
        Embed.add_field(name = 'Summary', value = summary, inline = False)
    else:
        list_summary = summary_split(summary, [])
        for i in range(len(list_summary)):
            para_number = i+1
            Embed.add_field(name = "Paragraph {}".format(para_number), value = list_summary[i], inline = False)

    await ctx.author.send(embed = Embed)


@client.command(name = 'newsletterCategory', aliases = ['nlc', 'nc'])
async def about(ctx, channel, *, category):
    messages = db.get_messages_with_category(message_collection, keywords_collection, ctx.guild.id, channel, category)
    summary = tfidf_summarizer.run_summarization(messages)

    Embed = discord.Embed(
        title = ("Newsletter from the " + channel + " channel in the " + ctx.guild.name + " server"),
        description = "*The summary is sent in multiple paragraphs due to size constrictions when sending it all in one paragraph*"
    )

    if len(summary)<1024:
        Embed.add_field(name = 'Summary', value = summary, inline = False)
    else:
        list_summary = summary_split(summary, [])
        for i in range(len(list_summary)):
            para_number = i+1
            Embed.add_field(name = "Paragraph {}".format(para_number), value = list_summary[i], inline = False)

    await ctx.author.send(embed = Embed)


@client.command(name = 'newsletterCategoryDay', aliases = ['nlcd', 'ncd'])
async def about(ctx, channel, date, *, category):
    messages = db.get_messages_with_category_specific_day(message_collection, keywords_collection, ctx.guild.id, channel, category, date)
    summary = tfidf_summarizer.run_summarization(messages)

    Embed = discord.Embed(
        title = ("Newsletter from the " + channel + " channel in the " + ctx.guild.name + " server"),
        description = "*The summary is sent in multiple paragraphs due to size constrictions when sending it all in one paragraph*"
    )

    if len(summary)<1024:
        Embed.add_field(name = 'Summary', value = summary, inline = False)
    else:
        list_summary = summary_split(summary, [])
        for i in range(len(list_summary)):
            para_number = i+1
            Embed.add_field(name = "Paragraph {}".format(para_number), value = list_summary[i], inline = False)

    await ctx.author.send(embed = Embed)


@client.event
async def on_message(message):

    if (message.author.bot):
        return
    if (message.author.id != message.author.bot):
        if(message.content.startswith("!") == False):
            db.add_all_messages(all_messages_collection, str(message.author),
                                message.created_at, message.content,
                                message.guild.id, str(message.channel.name))

            # Updates keyword list
            keywords_list = db.get_keywords(keywords_collection, message.guild.id)
            for key in keywords_list:
                if key in message.content:
                    keyword_found = key
                    print('Found')

                    # Adds message to the database if it has a keyword
                    db.add_message(message_collection,
                                   users_collection,
                                   str(message.author),
                                   keyword_found,
                                   message.content,
                                   message.guild.id,
                                   str(message.channel.name),
                                   message.created_at)
    await client.process_commands(message)



def summary_split(sum, original_list):
    list = original_list
    first_half = sum[:1024]
    second_half = sum[1024:]

    if len(sum)>1024:
        list.append(first_half)
        if len(second_half)>1024:
            return summary_split(second_half, list)
        else:
            list.append(second_half)
            return list
    else:
        list.append(first_half)
        list.append(second_half)
        return list





client.run(os.environ['DISCORD_TOKEN'])
