import json
import discord
from discord.ext import commands
from typing import Union


crown_emoji = "<:Crown:1149500405080915999>"
black_crown = "<:black_crown:1149501899196870706>"


def has_permission(author_id, allowed_roles, owners_data):
    return any(author_id in owners_data[role] for role in allowed_roles)


def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


class UserOrIdConverter(commands.MemberConverter):
    async def convert(self, ctx, argument):
        try:
            return await super().convert(ctx, argument)
        except commands.BadArgument:
            try:
                user_id = int(argument.strip('<@!>'))
                return await ctx.bot.fetch_user(user_id)
            except ValueError:
                raise commands.BadArgument(f'Could not convert "{argument}" to a user or user ID.')


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owners_data = None
        with open('owners.json', 'r') as f:
            self.owners_data = json.load(f)
        self.BLUE_COLOR = discord.Color(0x000000)
        self.GREEN_COLOR = discord.Color(0x000000)

    def load_owners_data(self):
        with open('owners.json', 'r') as owners_file:
            self.owners_data = json.load(owners_file)

    @commands.command(name='sys', help="Affiche/ajoute un liste des sys")
    async def manage_sys_list(self, ctx, user: Union[discord.Member, discord.User, None] = None):
        self.load_owners_data()

        author_id = str(ctx.author.id)

        if not has_permission(author_id, ["sys+"], self.owners_data):
            embed = discord.Embed(color=discord.Color(0x000000))
            embed.title = "Action refusée"
            embed.description = "Vous n'êtes pas autorisé à effectuer ceci."
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(color=self.BLUE_COLOR)

        if user is None:
            sys_list = [f"{idx + 1}. <@{user_id}>" for idx, user_id in enumerate(self.owners_data["sys"])]

            description = "\n".join(sys_list) if sys_list else "Aucun 'sys' défini."
            embed.title = f"{crown_emoji} Liste des SYS"
            embed.description = description
            await ctx.send(embed=embed)
        else:
            user_id = str(user.id)
            if user_id in self.owners_data["sys"]:
                self.owners_data["sys"].remove(user_id)
                save_to_file(self.owners_data, 'owners.json')
                embed.title = "Statut modifié"
                embed.description = f"<@{user.id}> a été retiré de la liste des 'sys'."
                await ctx.send(embed=embed)  # Envoi de l'embed
            else:
                self.owners_data["sys"].append(user_id)
                save_to_file(self.owners_data, 'owners.json')
                embed.title = "Statut modifié"
                embed.description = f"<@{user.id}> a été ajouté à la liste des 'sys'."
                await ctx.send(embed=embed)  # Envoi de l'embed

    @commands.command(name='owner', help="Affiche/ajoute un owner")
    async def manage_owner_status(self, ctx, user: Union[discord.Member, discord.User, None] = None):
        self.load_owners_data()

        author_id = str(ctx.author.id)

        if not has_permission(author_id, ["sys", "sys+"], self.owners_data):
            embed = discord.Embed(color=discord.Color(0x000000))
            embed.title = "Action refusée"
            embed.description = "Vous n'êtes pas autorisé à effectuer ceci."
            await ctx.send(embed=embed)
            return

        if user is None:
            owner_list = [f"{idx + 1}. <@{user_id}>" for idx, user_id in enumerate(self.owners_data["owner"])]

            description = "\n".join(owner_list) if owner_list else "Aucun Owner défini."
            embed = discord.Embed(title=f"{black_crown} Liste des OWNER", description=description, color=self.GREEN_COLOR)
            await ctx.send(embed=embed)
        else:
            user_id = str(user.id)
            embed = discord.Embed(color=self.GREEN_COLOR)
            if user_id in self.owners_data["owner"]:
                self.owners_data["owner"].remove(user_id)
                save_to_file(self.owners_data, 'owners.json')
                embed.title = "Statut modifié"
                embed.description = f"<@{user.id}> a été retiré de la liste des 'owners'."
                await ctx.send(embed=embed)
            else:
                self.owners_data["owner"].append(user_id)
                save_to_file(self.owners_data, 'owners.json')
                embed.title = "Statut modifié"
                embed.description = f"<@{user.id}> a été ajouté à la liste des 'owners'."
                await ctx.send(embed=embed)

    @commands.command(name='wl', help="Affiche/ajoute/retire un utilisateur de la whitelist")
    async def manage_whitelist(self, ctx, user: Union[discord.Member, discord.User, None] = None):
        self.load_owners_data()

        author_id = str(ctx.author.id)

        if not has_permission(author_id, ["owner"], self.owners_data):
            embed = discord.Embed(color=discord.Color(0x000000))
            embed.title = "Action refusée"
            embed.description = "Vous n'êtes pas autorisé à effectuer ceci."
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(color=self.BLUE_COLOR)

        if user is None:
            whitelist = [f"{idx + 1}. <@{user_id}>" for idx, user_id in enumerate(self.owners_data["whitelist"])]

            description = "\n".join(whitelist) if whitelist else "Aucun utilisateur dans la whitelist."
            embed.title = "Liste de la whitelist"
            embed.description = description
            await ctx.send(embed=embed)
        else:
            user_id = str(user.id)
            if user_id in self.owners_data["whitelist"]:
                self.owners_data["whitelist"].remove(user_id)
                save_to_file(self.owners_data, 'owners.json')
                embed.title = "Statut modifié"
                embed.description = f"<@{user.id}> a été retiré de la whitelist."
                await ctx.send(embed=embed)
            else:
                self.owners_data["whitelist"].append(user_id)
                save_to_file(self.owners_data, 'owners.json')
                embed.title = "Statut modifié"
                embed.description = f"<@{user.id}> a été ajouté à la whitelist."
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(OwnerCog(bot))
