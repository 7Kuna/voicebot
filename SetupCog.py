import json
import discord
from discord.ext import commands


async def is_owner(ctx):
    owner_cog = ctx.bot.get_cog('OwnerCog')

    if not owner_cog:
        embed = discord.Embed(title="Erreur", description="OwnerCog n'est pas chargé.", color=discord.Color(0x000000))
        await ctx.send(embed=embed)
        return False

    owner_ids = [int(id_str) for id_str in owner_cog.owners_data.get("owner", [])]

    if ctx.author.id not in owner_ids:
        embed = discord.Embed(title="Action refusée",
                              description="Vous n'avez pas les permissions nécessaires pour exécuter cette commande.",
                              color=discord.Color(0x000000))
        await ctx.send(embed=embed)
        return False

    return True


async def is_sys(ctx):
    owner_cog = ctx.bot.get_cog('OwnerCog')
    if not owner_cog:
        embed = discord.Embed(title="Erreur", description="OwnerCog n'est pas chargé.", color=discord.Color(0x000000))
        await ctx.send(embed=embed)
        return False

    sys_ids = [int(id_str) for id_str in owner_cog.owners_data.get("sys", [])]
    if ctx.author.id not in sys_ids:
        embed = discord.Embed(title="Action refusée", description="Vous n'avez pas les permissions nécessaires pour exécuter cette commande.", color=discord.Color(0x000000))
        await ctx.send(embed=embed)
        return False

    return True


class SetupCog(commands.Cog):

    def __init__(self, bot):
        self.cmd_config = None
        self.bot = bot
        self.reload_config()

    def reload_config(self):
        with open('setupconfig.json', 'r') as file:
            self.cmd_config = json.load(file)
            for key, value in self.cmd_config.items():
                self.cmd_config[key] = [int(role_id) for role_id in value]

    @commands.check(is_sys)
    @commands.command(name='setupclear', help='Efface complètement la configuration des setups')
    async def clear_setup_data(self, ctx):
        self.cmd_config = {}
        with open('setupconfig.json', 'w') as file:
            json.dump(self.cmd_config, file, indent=4)

        embed = discord.Embed(title="Succès", description="La configuration des setups a été effacée avec succès.",
                              color=discord.Color(0x000000))
        await ctx.send(embed=embed)

    @commands.check(is_owner)
    @commands.command(name='setup', help="Attribue une commande à un rôle ou affiche la liste des commandes attribuées ou la retire si elle est déjà attribuée.")
    async def setup_command(self, ctx, cmd_name: str = None, role: discord.Role = None):
        self.reload_config()
        if not cmd_name:
            embed = discord.Embed(title="Configuration actuelle", color=discord.Color(0x000000))

            for cmd in ['mv', 'join', 'find']:
                role_ids = self.cmd_config.get(cmd, [])
                role_mentions = [ctx.guild.get_role(role_id).mention for role_id in role_ids if
                                 ctx.guild.get_role(role_id)]
                roles_str = "\n".join(role_mentions) if role_mentions else ""
                embed.add_field(name=f"__**{cmd.upper()}**__", value=roles_str, inline=False)

            await ctx.send(embed=embed)
            return

        if not role:
            embed = discord.Embed(title="Erreur", description="Vous devez mentionner un rôle ou fournir son ID.",
                                  color=discord.Color(0x000000))
            await ctx.send(embed=embed)
            return

        if cmd_name not in ['mv', 'join', 'find']:
            embed = discord.Embed(title="Erreur",
                                  description="Nom de commande invalide. Les commandes valides sont: `mv`, `join`, `find`.",
                                  color=discord.Color(0x000000))
            await ctx.send(embed=embed)
            return

        role_list = self.cmd_config.get(cmd_name, [])
        if role.id in role_list:
            role_list.remove(role.id)
            action_msg = f"La commande `{cmd_name}` a été retirée du rôle {role.mention}."
        else:
            role_list.append(role.id)
            action_msg = f"La commande `{cmd_name}` a été attribuée au rôle {role.mention}."

        self.cmd_config[cmd_name] = role_list

        with open('setupconfig.json', 'w') as file:
            json.dump(self.cmd_config, file, indent=4)

        embed = discord.Embed(title="Succès",
                              description=action_msg,
                              color=discord.Color(0x000000))
        await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(SetupCog(bot))
