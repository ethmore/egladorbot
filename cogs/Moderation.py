import nextcord
from nextcord.ext import commands
import config
from nextcord import Interaction, SlashOption


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = self.client.get_channel(message.channel.id)

        if config.channelSelectivity is True:  # Channel selectivity check
            if channel.name == config.selectedChannel and not message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel TRUE, prefix FALSE, message NOT belongs to the bot
                config.allowMessages = False
            elif channel.name != config.selectedChannel and message.content.startswith(config.commandPrefix) and message.author != self.client.user:
                await message.delete()  # Channel FALSE, prefix TRUE, message NOT belongs to the bot
                config.allowMessages = False
        else:
            config.allowMessages = False

        # Forbidden word detection
        guildID = message.guild.id
        user_id = message.author.id
        split_message = message.content.split(" ")
        db_forbidden_words = config.db_forbidden.count_documents({"server_id": guildID, "forbidden_word": {"$in": split_message}})
        user_warn_count = int(0)
        channel_role_ids = list([])

        for x in message.author.roles:
            channel_role_ids.append(x.id)
        excluded_roles = config.db_excluded_roles.count_documents({"server_id": guildID, "excepted_role": {"$in": channel_role_ids}})

        if message.author != self.client.user or message.author.guild_permissions.administrator is not True or excluded_roles > 0:
            if db_forbidden_words > 0:
                db_auto_warn_active = config.db_config.find_one({"server_id": guildID})

                if db_auto_warn_active["server_auto_warn"] == "activate":
                    user_warn_count = config.db_warn_counts.find_one({"server_id": guildID, "user_id": user_id})
                    if not user_warn_count:
                        config.db_warn_counts.insert_one({"server_id": guildID, "user_id": user_id, "warn_count": 1})
                        await channel.send(f"That's forbidden! <@{user_id}> earned a warn")
                    else:
                        user_warn_count = user_warn_count["warn_count"] + 1
                        config.db_warn_counts.find_one_and_update({"server_id": guildID, "user_id": user_id},
                                                                  {"$set": {"warn_count": user_warn_count}})
                        await channel.send(f"@Noice <@{user_id}>! That makes {user_warn_count} warns.(Language)")
                else:
                    await channel.send("You shouldn't use that word but who cares")

            if config.db_config.count_documents({"server_id": guildID, "server_auto_kick": "activate"}):
                if user_warn_count > 2:
                    await channel.send(f"When warn count reached to 3 you are gonna be kicked by <@{self.client.user.id}>")
                    try:
                        await message.author.kick(reason="Warn count reached to 3")
                    except nextcord.errors.Forbidden:
                        await channel.send("I don't have permissions to kick this member")

            if config.db_config.count_documents({"server_id": guildID, "server_auto_ban": "activate"}):
                await channel.send(f"When warn count reached to 6 you are gonna be banned from server by <@{self.client.user.id}>")
                await message.author.ban(reason="Warn count reached to 6")

        else:
            pass  # That's me!

    @nextcord.slash_command(name="test", description="Up Test", guild_ids=config.guildID)
    async def test(self, interaction: Interaction):
        await interaction.send("Online", delete_after=5)
        pass

    # WIP - WIP - WIP - WIP - WIP - WIP
    @nextcord.slash_command(name="delete", description="[WIP] Deletes message", guild_ids=config.guildID)
    async def delete(self, interaction: Interaction):
        # author = ctx.message.author
        await interaction.message.delete()
        await interaction.send("Deleted [WIP]")

    # Forbidden words system {add, delete, list, update}
    @nextcord.slash_command(name="forbidden", description="Add or Delete a word from the forbidden words list", guild_ids=config.guildID)
    async def forbidden(self, interaction: Interaction,
                        statement: str = SlashOption(description="Select add or delete",
                                                     choices={"Add": "add", "Delete": "delete"}),
                        word=str()):
        match statement:
            case "add":
                guildID = interaction.guild_id
                db_guild_word = config.db_forbidden.find_one({"server_id": guildID, "forbidden_word": word})
                if not db_guild_word:
                    config.db_forbidden.insert_one({"server_id": guildID, "forbidden_word": word})
                    await interaction.send("Word is added to the forbidden word list")
                else:
                    await interaction.send("Word is already in list")

            case "delete":
                guildID = interaction.guild_id
                db_guild_word = config.db_forbidden.find_one_and_delete({"server_id": guildID, "forbidden_word": word})
                if db_guild_word:
                    await interaction.send("Word is removed from list")
                else:
                    await interaction.send("Word is not in the forbidden list")

    @nextcord.slash_command(name="forbidden_listall", description="Lists all forbidden words", guild_ids=config.guildID)
    async def forbidden_listall(self, interaction: Interaction):
        guildID = interaction.guild_id
        forbidden_list_message = str("")
        db_guild_words = config.db_forbidden.find({"server_id": guildID}, {"_id": 0, "server_id": 0})

        for x in db_guild_words:
            forbidden_list_message += f"``{x['forbidden_word']}``, "
        forbidden_list_message = forbidden_list_message[:-2]

        if forbidden_list_message:
            embeds = nextcord.Embed(title=forbidden_list_message, color=0x4dff4d)
            await interaction.send(embed=embeds)
        else:
            await interaction.send("There is no forbidden words")

    @nextcord.slash_command(name="forbidden_update", description="Updates an existing word", guild_ids=config.guildID)
    async def forbidden_update(self, interaction: Interaction, old_word, new_word):
        guildID = interaction.guild_id
        db_guild_word = config.db_forbidden.find_one_and_update({"server_id": guildID, "forbidden_word": old_word},
                                                                {"$set": {"forbidden_word": new_word}})

        if db_guild_word:
            await interaction.send("Word is updated")
        else:
            await interaction.send(f"There is no such word as ``{old_word}`` in the list")

    # Auto moderation {warn, kick, ban, status}
    @nextcord.slash_command(description="Activate or Deactivate auto moderation systems", guild_ids=config.guildID)
    async def auto_moderation(self, interaction: Interaction,
                              feature_type: str = SlashOption(description="Select feature that you want to manage",
                                                              choices={"Auto Warn": "auto_warn", "Auto Kick": "auto_kick", "Auto Ban": "auto_ban"}),
                              activate_deactivate: str = SlashOption(description="Activate or Deactivate the selected feature",
                                                                     choices={"Activate": "activate", "Deactivate": "deactivate"})):
        guildID = interaction.guild_id
        db_auto_warn_activated = config.db_config.find_one({"server_id": guildID})

        match feature_type:
            case "auto_warn":
                match activate_deactivate:
                    case "activate":
                        if not db_auto_warn_activated:
                            config.db_config.insert_one({"server_id": guildID,
                                                         "server_auto_warn": activate_deactivate, "server_auto_kick": " ", "server_auto_ban": " "})
                            await interaction.send("Auto warn system activated!")

                        else:
                            if db_auto_warn_activated["server_auto_warn"] == "activate":
                                await interaction.send("Auto warn system is already activated.")
                            else:
                                config.db_config.find_one_and_update({"server_id": guildID}, {"$set": {"server_auto_warn": "activate"}})
                                await interaction.send("Auto warn system activated.")

                    case "deactivate":
                        if not db_auto_warn_activated:
                            config.db_config.insert_one({"server_id": guildID,
                                                         "server_auto_warn": activate_deactivate, "server_auto_kick": " ", "server_auto_ban": " "})
                            await interaction.send("Auto warn system deactivated!")
                        else:
                            if db_auto_warn_activated["server_auto_warn"] == "deactivate":
                                await interaction.send("Auto warn system is already deactivated.")
                            else:
                                config.db_config.find_one_and_update({"server_id": guildID}, {"$set": {"server_auto_warn": "deactivate"}})
                                await interaction.send("Auto warn system deactivated.")

            case "auto_kick":
                match activate_deactivate:
                    case "activate":
                        if not db_auto_warn_activated:
                            config.db_config.insert_one({"server_id": guildID,
                                                         "server_auto_warn": " ", "server_auto_kick": activate_deactivate, "server_auto_ban": " "})
                            await interaction.send("Auto kick system activated!")

                        else:
                            if db_auto_warn_activated["server_auto_kick"] == "activate":
                                await interaction.send("Auto kick system is already activated.")
                            else:
                                config.db_config.find_one_and_update({"server_id": guildID}, {"$set": {"server_auto_kick": "activate"}})
                                await interaction.send("Auto kick system activated.")

                    case "deactivate":
                        if not db_auto_warn_activated:
                            config.db_config.insert_one({"server_id": guildID,
                                                         "server_auto_warn": " ", "server_auto_kick": activate_deactivate, "server_auto_ban": " "})
                            await interaction.send("Auto kick system deactivated!")
                        else:
                            if db_auto_warn_activated["server_auto_kick"] == "deactivate":
                                await interaction.send("Auto kick system is already deactivated.")
                            else:
                                config.db_config.find_one_and_update({"server_id": guildID}, {"$set": {"server_auto_kick": "deactivate"}})
                                await interaction.send("Auto kick system deactivated.")

            case "auto_ban":
                match activate_deactivate:
                    case "activate":
                        if not db_auto_warn_activated:
                            config.db_config.insert_one({"server_id": guildID,
                                                         "server_auto_warn": " ", "server_auto_kick": " ", "server_auto_ban": activate_deactivate})
                            await interaction.send("Auto ban system activated!")

                        else:
                            if db_auto_warn_activated["server_auto_ban"] == "activate":
                                await interaction.send("Auto ban system is already activated.")
                            else:
                                config.db_config.find_one_and_update({"server_id": guildID}, {"$set": {"server_auto_ban": "activate"}})
                                await interaction.send("Auto ban system activated.")

                    case "deactivate":
                        if not db_auto_warn_activated:
                            config.db_config.insert_one({"server_id": guildID,
                                                         "server_auto_warn": " ", "server_auto_kick": " ", "server_auto_ban": activate_deactivate})
                            await interaction.send("Auto ban system deactivated!")
                        else:
                            if db_auto_warn_activated["server_auto_ban"] == "deactivate":
                                await interaction.send("Auto ban system is already deactivated.")
                            else:
                                config.db_config.find_one_and_update({"server_id": guildID}, {"$set": {"server_auto_ban": "deactivate"}})
                                await interaction.send("Auto ban system deactivated.")
                        pass
                pass
        pass

    @nextcord.slash_command(name="auto_moderation_status", description="Shows current auto moderation status", guild_ids=config.guildID)
    async def get_auto_moderation(self, interaction: Interaction):
        guildID = interaction.guild_id
        a_moderation = config.db_config.find_one({"server_id": guildID})
        if not a_moderation:
            await interaction.send("There is no auto moderation features activated right now")
        else:
            embed = nextcord.Embed(title="Auto Moderation Feature Status", color=0x4dff4d)

            if a_moderation["server_auto_warn"] != " ":
                if a_moderation["server_auto_warn"] == "activate":
                    embed.add_field(name="Auto Warn", value="Activated", inline=False)
                else:
                    embed.add_field(name="Auto Warn", value="Deactivated", inline=False)

            if a_moderation["server_auto_kick"] != " ":
                if a_moderation["server_auto_kick"] == "activate":
                    embed.add_field(name="Auto Kick", value="Activated", inline=False)
                else:
                    embed.add_field(name="Auto Kick", value="Deactivated", inline=False)

            if a_moderation["server_auto_ban"] != " ":
                if a_moderation["server_auto_ban"] == "activate":
                    embed.add_field(name="Auto Ban", value="Activated", inline=False)
                else:
                    embed.add_field(name="Auto Ban", value="Deactivated", inline=False)

            embed.set_footer(text="You can use /auto_moderation command to manage auto moderation system status")
            await interaction.send(embed=embed)

    # Warn system {add, decrease, delete all, get count}
    @nextcord.slash_command(description="You can use this commands to add warn, decrease warn, delete warns and to get warn count of a user",
                            guild_ids=config.guildID)
    async def warn(self, interaction: Interaction,
                   statement: str = SlashOption(description="Select an option",
                                                choices={"Add": "add", "Decrease": "decrease", "Remove All": "remove_all", "Warn Count": "warn_count"}),
                   mention: nextcord.Member = SlashOption(name="user", description="Select a user")):
        guildID = interaction.guild_id
        user = config.db_warn_counts.find_one({"server_id": guildID, "user_id": mention.id})

        match statement:
            case "add":
                if not user:  # Add to db
                    config.db_warn_counts.insert_one({"server_id": guildID, "user_id": mention.id, "warn_count": 1})
                    await interaction.send("Warn added to the member. First warn")
                else:  # Update db
                    warn_count = user["warn_count"] + 1
                    config.db_warn_counts.update_one({"server_id": guildID, "user_id": mention.id}, {"$set": {"warn_count": warn_count}})
                    await interaction.send("Warn added to the member")

            case "decrease":
                if not user:
                    await interaction.send("Member has no warns")
                else:
                    if user["warn_count"] > 0:
                        warn_count = user["warn_count"] - 1
                        config.db_warn_counts.update_one({"server_id": guildID, "user_id": mention.id}, {"$set": {"warn_count": warn_count}})
                        await interaction.send(f"Member's warn count decreased by 1. Member now has {warn_count} warn/s")
                    else:
                        await interaction.send("Member has no warns")

            case "remove_all":
                if not user:
                    await interaction.send("Member has no warns")
                else:
                    if user["warn_count"] > 0:
                        config.db_warn_counts.update_one({"server_id": guildID, "user_id": mention.id}, {"$set": {"warn_count": 0}})
                        await interaction.send("Member's all warns removed")
                    else:
                        await interaction.send("Member has no warns")

            case "warn_count":
                if not user:
                    await interaction.send("Member has no warns")
                else:
                    if user['warn_count'] == 0:
                        await interaction.send("Member has no warns")
                    else:
                        await interaction.send(f"Member has {user['warn_count']} warn/s")

    # Role exception system {add, remove, list}
    @nextcord.slash_command(description="Excluded roles from auto moderation features", guild_ids=config.guildID)
    async def allowed_role(self, interaction: Interaction,
                           statement: str = SlashOption(description="Add or remove role from allowed roles",
                                                        choices={"Add role": "add", "Remove role": "remove"}),
                           role_mention: nextcord.Role = SlashOption(name="role", description="Select a role")):

        guildID = interaction.guild_id
        match statement:
            case "add":
                excluded_role_db = config.db_excluded_roles.find_one({"server_id": guildID, "excepted_role": role_mention.id})
                if not excluded_role_db:
                    config.db_excluded_roles.insert_one({"server_id": guildID, "excepted_role": role_mention.id})
                    await interaction.send("Role added to the exception list")
                else:
                    await interaction.send("Role is already in the exception list")

            case "remove":
                role_removed = config.db_excluded_roles.find_one_and_delete({"server_id": guildID, "excepted_role": role_mention.id})
                if role_removed:
                    await interaction.send("Role is removed from the exception list")
                else:
                    await interaction.send("Role is not in the exception list")
                pass

    @nextcord.slash_command(name="role_exception_list", description="Lists all excluded roles from auto moderation system", guild_ids=config.guildID)
    async def excepted_role_list(self, interaction: Interaction):
        guildID = interaction.guild_id
        excluded_roles_msg = "Excluded role/s: "
        excluded_roles = config.db_excluded_roles.find({"server_id": guildID})

        for x in excluded_roles:
            excluded_roles_msg += f"<@&{x['excepted_role']}>, "
        excluded_roles_msg = excluded_roles_msg[:-2]

        if excluded_roles_msg:
            await interaction.send(excluded_roles_msg)
        else:
            await interaction.send("There is no excluded roles")


def setup(client):
    client.add_cog(Moderation(client))
