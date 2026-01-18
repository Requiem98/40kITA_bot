import discord
from discord import app_commands
import os

ROLE_NAMES = {
    # LFG
    "LFG": "LFG",
    "LFG Beginner": "LFG Beginner",

    # Factions
    "SM": "Adeptus Astartes",
    "BA": "Blood Angels",
    "DA": "Dark Angels",
    "SW": "Space Wolves",
    "BT": "Black Templars",
    "DW": "Deathwatch",
    "AC": "Adeptus Custodes",
    "AS": "Adepta Sororitas",
    "GK": "Grey Knights",
    "IK": "Imperial Knights",
    "adMech": "Adeptus Mechanicus",
    "AM": "Astra Militarium",
    "CSM": "Chaos Marines",
    "DG": "Death Guard",
    "TS": "Thousand Sons",
    "WE": "World Eaters",
    "EC": "Emperors Children",
    "CD": "Chaos Deamons",
    "CK": "Chaos Knights",
    "CW": "Aeldari",
    "Drukh": "Drukhari",
    "GSC": "Genestealer Cults",
    "LoV": "Leagues of Votann",
    "Necr": "Necrons",
    "Orks": "Orks",
    "TAU": "T'au Empire",
    "Nids": "Tyranids",
}

FACTION_CHANNELS = {
    "SM": "adeptus-astartes",
    "BA": "blood-angels",
    "DA": "dark-angels",
    "SW": "space-wolves",
    "BT": "black-templars",
    "DW": "deathwatch",
    "AC": "adeptus-custodes",
    "AS": "adepta-sororitas",
    "GK": "grey-knights",
    "IK": "imperial-knights",
    "adMech": "adeptus-mechanicus",
    "AM": "astra-militarum",
    "CSM": "chaos-marines",
    "DG": "death-guard",
    "TS": "thousand-sons",
    "WE": "world-eaters",
    "EC": "emperors-children",
    "CD": "chaos-daemons",
    "CK": "chaos-knights",
    "CW": "aeldari",
    "Drukh": "drukhari",
    "GSC": "genestealer-cults",
    "LoV": "leagues-of-votann",
    "Necr": "necrons",
    "Orks": "orks",
    "TAU": "tau-empire",
    "Nids": "tyranids",
}

class RoleView(discord.ui.View):
    def __init__(self, guild: discord.Guild, role_type:str):
        super().__init__()
        
        self.role_map = {
            key: discord.utils.get(guild.roles, name=name)
            for key, name in ROLE_NAMES.items()
        }

        if(role_type == "LFG match"):
            select = discord.ui.Select(
                        placeholder="Seleziona a quali partite vuoi ricevere notifiche.",
                        min_values=0,
                        max_values=2,
                        options=[
                            discord.SelectOption(label="@LFG", value="LFG"),
                            discord.SelectOption(label="@LFG Beginner", value="LFG Beginner")
                        ],
                        custom_id="role_select")
            
        elif(role_type == "Faction"):
            options = [discord.SelectOption(label=name, value=key) for key, name in self.role_map.items() if key not in ["LFG", "LFG Beginner"]]
            select = discord.ui.Select(
                        placeholder="Seleziona le fazioni che preferisci giocare",
                        min_values=0,
                        max_values=27,
                        options=options,
                        custom_id="faction_select"
                    )
        select.callback = self.select_callback
        self.add_item(select)
        
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        member = interaction.user

        selected = {self.role_map[v] for v in select.values if self.role_map[v]}
        managed = set(self.role_map.values())

        for role in managed:
            if role and role in member.roles and role not in selected:
                await member.remove_roles(role)

        for role in selected:
            if role not in member.roles:
                await member.add_roles(role)

        await interaction.response.send_message(
            "Roles updated.",
            ephemeral=True
        )

async def ensure_roles_exist(guild: discord.Guild):
    for role_name in ROLE_NAMES.values():
        if discord.utils.get(guild.roles, name=role_name) is None:
            await guild.create_role(name=role_name, reason="Auto-created by role selection bot")

async def ensure_factions_category(guild: discord.Guild) -> discord.CategoryChannel:
    category = discord.utils.get(guild.categories, name="Factions")
    if category:
        return category

    return await guild.create_category(
        name="Factions",
        reason="Auto-created faction category"
    )

async def ensure_faction_channels_exist(guild: discord.Guild):
    everyone = guild.default_role
    category = await ensure_factions_category(guild)

    for key, channel_name in FACTION_CHANNELS.items():
        role = discord.utils.get(guild.roles, name=ROLE_NAMES[key])
        if role is None:
            continue

        channel = discord.utils.get(
            guild.text_channels,
            name=channel_name
        )
        if channel:
            continue

        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False),
            role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
        }

        await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason="Auto-created faction channel"
        )

@discord.app_commands.default_permissions(administrator=True)
class BotCommands(app_commands.Group):
    @app_commands.command(name="roles", description="Send the role selection menu")
    async def roles(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Role Selection",
            description="Choose your roles below."
        )
        await interaction.response.send_message(embed=embed, view=RoleView(interaction.guild, "LFG match"))
        
    @app_commands.command(name="factions", description="Send the factions selection menu")
    async def factions(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Faction Selection",
            description="Choose your factions below."
        )
        await interaction.response.send_message(embed=embed, view=RoleView(interaction.guild, "Faction"))


class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.add_command(BotCommands())
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot online: {self.user}")
        for guild in bot.guilds:
            await ensure_roles_exist(guild)
            await ensure_faction_channels_exist(guild)
            self.add_view(RoleView(guild, "LFG match"))
            self.add_view(RoleView(guild, "Faction"))
        
    async def on_guild_join(self, guild: discord.Guild):
        print(f"Joined new guild: {guild.name} ({guild.id})")
        print("ensure roles exist...")
        await ensure_roles_exist(guild)
        print("ensure faction channels exist...")
        await ensure_faction_channels_exist(guild)
        print("Done!")

bot = Bot()
bot.run(os.getenv("DISCORD_TOKEN"))
