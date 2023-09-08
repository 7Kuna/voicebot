import discord
from discord.ext import commands
import json
import random


class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mv')
    async def move_member(self, ctx, member: discord.Member, channel: discord.VoiceChannel = None):
        try:
            with open('setupconfig.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            embed = discord.Embed(
                title="Erreur",
                description="Fichier setup introuvable sanoo tu sais pas mettre des fichiers",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return
        except json.JSONDecodeError:
            embed = discord.Embed(
                title="Erreur",
                description="La config est pas faite",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if 'mv' not in data:
            embed = discord.Embed(
                title="Configuration manquante",
                description="Il n'y a pas de config",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if not any(role.id in data['mv'] for role in ctx.author.roles):
            embed = discord.Embed(
                title="Accès refusé",
                description="Vous n'avez pas les permissions nécessaires pour utiliser cette commande.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if not channel:
            if not ctx.author.voice or not ctx.author.voice.channel:
                embed = discord.Embed(
                    title="Erreur",
                    description="Vous devez être dans un salon vocal ou spécifier un canal pour utiliser cette commande.",
                    color=discord.Color(0x000000)
                )
                await ctx.send(embed=embed)
                return
            target_channel = ctx.author.voice.channel
        else:
            target_channel = channel

        try:
            await member.move_to(target_channel)
            embed = discord.Embed(
                title="Membre déplacé",
                description=f"L'utilisateur {member.mention} a bien été move dans le salon {target_channel.mention}.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Erreur",
                description=f"{e}",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def join(self, ctx, target):
        member = None
        if target.startswith('<@') and target.endswith('>'):
            member_id = target.strip('<@!>')
            member = ctx.guild.get_member(int(member_id))
        else:
            try:
                member_id = int(target)
                member = ctx.guild.get_member(member_id)
            except ValueError:
                pass

        if not member:
            embed = discord.Embed(
                title="Erreur",
                description=f"L'utilisateur avec l'ID ou la mention {target} n'a pas été trouvé.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if not member.voice or not member.voice.channel:
            embed = discord.Embed(
                title="Erreur",
                description=f"L'utilisateur {member.mention} n'est pas dans un salon vocal.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        try:
            await ctx.author.move_to(member.voice.channel)
            embed = discord.Embed(
                title="Vous avez rejoint le salon",
                description=f"Vous avez bien été déplacé dans le salon {member.voice.channel.mention}.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Erreur",
                description=f"{e}",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def find(self, ctx, target):
        try:
            with open('setupconfig.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            embed = discord.Embed(
                title="Erreur",
                description="Fichier setup introuvable. Assurez-vous qu'il est bien en place.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return
        except json.JSONDecodeError:
            embed = discord.Embed(
                title="Erreur",
                description="La config est mal formatée ou incomplète.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if 'find' not in data:
            embed = discord.Embed(
                title="Configuration manquante",
                description="Il n'y a pas de config pour la commande find.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if not any(role.id in data['find'] for role in ctx.author.roles):
            embed = discord.Embed(
                title="Accès refusé",
                description="Vous n'avez pas les permissions nécessaires pour utiliser cette commande.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return
        member = None
        if target.startswith('<@') and target.endswith('>'):
            member_id = target.strip('<@!>')
            member = ctx.guild.get_member(int(member_id))
        else:
            try:
                member_id = int(target)
                member = ctx.guild.get_member(member_id)
            except ValueError:
                pass

        if not member:
            embed = discord.Embed(
                title="Erreur",
                description=f"L'utilisateur avec l'ID ou la mention {target} n'a pas été trouvé.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if member.voice and member.voice.channel:
            embed = discord.Embed(
                title=f"{member.name} a été trouvé",
                description=f"{member.mention} est actuellement dans {member.voice.channel.mention}.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"{member.name} n'est pas en vocal",
                description=f"{member.mention} n'est actuellement dans aucun salon vocal.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def wakeup(self, ctx, target):
        try:
            with open('owners.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            embed = discord.Embed(
                title="Erreur",
                description="Fichier 'owners.json' introuvable.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return
        except json.JSONDecodeError:
            embed = discord.Embed(
                title="Erreur",
                description="Problème de lecture du fichier 'owners.json'.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if str(ctx.author.id) not in data['sys']:
            embed = discord.Embed(
                title="Accès refusé",
                description="Vous n'avez pas la permission d'utiliser cette commande.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        member = None
        if target.startswith('<@') and target.endswith('>'):
            member_id = target.strip('<@!>')
            member = ctx.guild.get_member(int(member_id))
        else:
            try:
                member_id = int(target)
                member = ctx.guild.get_member(member_id)
            except ValueError:
                pass

        if not member:
            embed = discord.Embed(
                title="Erreur",
                description=f"L'utilisateur avec l'ID ou la mention {target} n'a pas été trouvé.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        if not member.voice or not member.voice.channel:
            embed = discord.Embed(
                title="Erreur",
                description=f"{member.mention} n'est pas en vocal.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        initial_channel = member.voice.channel
        voice_channels = [channel for channel in ctx.guild.voice_channels if channel.permissions_for(ctx.me).connect]
        if len(voice_channels) < 2:
            embed = discord.Embed(
                title="Erreur",
                description="Pas assez de salons vocaux sur le serveur pour exécuter la commande.",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"{member.name} se fait réveiller!",
            description=f"{member.mention} va être déplacé dans différents salons vocaux!",
            color=discord.Color(0x000000)
        )
        await ctx.send(embed=embed)

        try:
            for i in range(10):
                target_channel = random.choice([ch for ch in voice_channels if ch != member.voice.channel])
                await member.move_to(target_channel)
            await member.move_to(initial_channel)
        except Exception as e:
            embed = discord.Embed(
                title="Erreur",
                description=f"Erreur lors du déplacement de l'utilisateur: {e}",
                color=discord.Color(0x000000)
            )
            await ctx.send(embed=embed)
            return


def setup(bot):
    bot.add_cog(MiscCog(bot))
