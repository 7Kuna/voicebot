import discord
from discord.ext import commands
import json


async def is_role(ctx, role_name):
    owner_cog = ctx.bot.get_cog('OwnerCog')
    if not owner_cog:
        await ctx.send(embed=discord.Embed(title="Erreur", description="OwnerCog n'est pas chargé.",
                                           color=discord.Color(0x000000)))
        return False

    role_ids = [int(id_str) for id_str in owner_cog.owners_data.get(role_name, [])]
    if ctx.author.id not in role_ids:
        await ctx.send(embed=discord.Embed(title="Action refusée", description="Permissions insuffisantes.",
                                           color=discord.Color(0x000000)))
        return False

    return True


async def is_owner(ctx):
    return await is_role(ctx, "owner")


async def is_sys(ctx):
    return await is_role(ctx, "sys")


async def is_channel_in_locked_category(channel):
    with open('catlock.json', 'r') as file:
        data = json.load(file)
    return any(item["category_id"] == str(channel.category_id) for item in data["locked_categories"])


class PrivateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.private_channels = {}

    @commands.check(is_owner)
    @commands.command()
    async def pv(self, ctx):
        if await is_channel_in_locked_category(ctx.channel):
            await ctx.send(embed=discord.Embed(title="Erreur", description="Commande désactivée dans cette catégorie.",
                                               color=discord.Color(0x000000)))
            return

        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            if channel.id in self.private_channels:
                if self.private_channels[channel.id]['owner'] == ctx.author.id:
                    del self.private_channels[channel.id]
                    await ctx.send(embed=discord.Embed(title="Salon vocal public",
                                                       description=f"<#{channel.id}> est maintenant public.",
                                                       color=discord.Color(0x000000)))
                else:
                    await ctx.send(embed=discord.Embed(title="Erreur",
                                                       description=f"Vous n'avez pas le droit de modifier le statut de <#{channel.id}>.",
                                                       color=discord.Color(0x000000)))
            else:
                self.private_channels[channel.id] = {"owner": ctx.author.id, "allowed": [ctx.author.id]}
                await ctx.send(
                    embed=discord.Embed(title="Salon vocal privé", description=f"<#{channel.id}> est maintenant privé.",
                                        color=discord.Color(0x000000)))
        else:
            await ctx.send(embed=discord.Embed(title="Erreur", description="Vous devez être dans un salon vocal.",
                                               color=discord.Color(0x000000)))

    @commands.check(is_owner)
    @commands.command()
    async def pvlist(self, ctx):
        if not self.private_channels:
            await ctx.send(embed=discord.Embed(title="Salons privés", description="Aucun salon privé actuellement.",
                                               color=discord.Color(0x000000)))
            return
        description = "\n".join([f"Salon: <#{channel_id}>, Propriétaire: <@{data['owner']}>" for channel_id, data in
                                 self.private_channels.items()])
        await ctx.send(
            embed=discord.Embed(title="Salons vocaux privés", description=description, color=discord.Color(0x000000)))

    @commands.check(is_sys)
    @commands.command()
    async def pvdelete(self, ctx):
        self.private_channels.clear()
        await ctx.send(embed=discord.Embed(title="Réinitialisation",
                                           description="Tous les salons vocaux privés ont été réinitialisés.",
                                           color=discord.Color(0x000000)))

    @commands.check(is_owner)
    @commands.command()
    async def access(self, ctx, member: discord.Member = None):
        if await is_channel_in_locked_category(ctx.channel):
            await ctx.send(embed=discord.Embed(title="Erreur", description="Commande désactivée dans cette catégorie.",
                                               color=discord.Color(0x000000)))
            return

        if ctx.author.voice and ctx.author.voice.channel:
            channel_id = ctx.author.voice.channel.id

            if channel_id not in self.private_channels:
                await ctx.send(embed=discord.Embed(title="Erreur", description="Ce salon n'est pas pv.",
                                                   color=discord.Color(0x000000)))
                return

            if self.private_channels[channel_id]['owner'] == ctx.author.id:
                if not member:
                    allowed_members = self.private_channels[channel_id]['allowed']
                    if not allowed_members:
                        await ctx.send(embed=discord.Embed(title="Accès",
                                                           description="Personne n'a accès à ce salon privé.",
                                                           color=discord.Color(0x000000)))
                        return
                    allowed_mentions = " ".join([f"<@{user_id}>" for user_id in allowed_members])
                    await ctx.send(embed=discord.Embed(title="Accès",
                                                       description=f"Utilisateurs ayant accès : {allowed_mentions}",
                                                       color=discord.Color(0x000000)))
                    return

                if member.id in self.private_channels[channel_id]['allowed']:
                    self.private_channels[channel_id]['allowed'].remove(member.id)
                    await ctx.send(embed=discord.Embed(title="Accès retiré",
                                                       description=f"{member.mention} n'a plus accès à <#{channel_id}>.",
                                                       color=discord.Color(0x000000)))
                else:
                    self.private_channels[channel_id]['allowed'].append(member.id)
                    await ctx.send(embed=discord.Embed(title="Accès accordé",
                                                       description=f"{member.mention} a maintenant accès à <#{channel_id}>.",
                                                       color=discord.Color(0x000000)))
            else:
                await ctx.send(embed=discord.Embed(title="Erreur",
                                                   description="Vous n'avez pas le droit de modifier l'accès à ce salon.",
                                                   color=discord.Color(0x000000)))
        else:
            await ctx.send(embed=discord.Embed(title="Erreur", description="Vous devez être dans un salon vocal.",
                                               color=discord.Color(0x000000)))

    @commands.check(is_sys)
    @commands.command()
    async def catlock(self, ctx, category_id: int = None):
        try:
            with open('catlock.json', "r") as file:
                data = json.load(file)

            if not category_id:
                if not data["locked_categories"]:
                    await ctx.send(embed=discord.Embed(title="Catégories verrouillées",
                                                       description="Il n'y a actuellement aucune catégorie verrouillée.",
                                                       color=discord.Color(0x000000)))
                    return

                description = "\n".join([f"<#{cat['category_id']}>" for cat in data["locked_categories"]])
                await ctx.send(embed=discord.Embed(title="Catégories verrouillées",
                                                   description=description,
                                                   color=discord.Color(0x000000)))
                return

            category = next((item for item in data["locked_categories"] if item["category_id"] == str(category_id)),
                            None)

            if category:
                data["locked_categories"].remove(category)
                await ctx.send(embed=discord.Embed(title="Catégorie déverrouillée",
                                                   description=f"La catégorie <#{category_id}> et tous ses salons vocaux sont maintenant publics.",
                                                   color=discord.Color(0x000000)))
            else:
                cat_obj = ctx.guild.get_channel(category_id)
                if not cat_obj or not isinstance(cat_obj, discord.CategoryChannel):
                    await ctx.send(embed=discord.Embed(title="Erreur",
                                                       description="ID de catégorie invalide.",
                                                       color=discord.Color(0x000000)))
                    return

                voice_channels = [chan.id for chan in cat_obj.voice_channels]
                data["locked_categories"].append({"category_id": str(category_id), "channel_ids": voice_channels})
                await ctx.send(embed=discord.Embed(title="Catégorie verrouillée",
                                                   description=f"La catégorie <#{category_id}> et tous ses salons vocaux sont maintenant privés.",
                                                   color=discord.Color(0x000000)))

            with open('catlock.json', 'w') as file:
                json.dump(data, file)
        except Exception as e:
            await ctx.send(f"Une erreur est survenue: {str(e)}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not after.channel:
            return

        with open('catlock.json', 'r') as file:
            data = json.load(file)

        category = next((item for item in data["locked_categories"] if after.channel.id in item["channel_ids"]), None)

        if category:
            with open('owners.json', 'r') as owner_file:
                owner_data = json.load(owner_file)

            if str(member.id) not in owner_data["whitelist"]:
                await member.move_to(None)
                try:
                    await member.send(
                        "Vous n'avez pas l'autorisation de rejoindre ce salon vocal car la catégorie est verrouillée.")
                except discord.errors.Forbidden:
                    print(f"Couldn't send message to {member.name}")
                return

        if after.channel.id in self.private_channels and member.id not in self.private_channels[after.channel.id][
            "allowed"]:
            await member.move_to(None)


def setup(bot):
    bot.add_cog(PrivateCog(bot))
