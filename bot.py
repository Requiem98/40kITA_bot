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

class RoleView(discord.ui.View):
    def __init__(self, role_type:str):
        super().__init__()
        await ensure_roles_exist(guild)
        self.role_map = {
            key: discord.utils.get(guild.roles, name=name)
            for key, name in ROLE_NAMES.items()
        }

        if(role_type == "LFG match"):
            @discord.ui.select(
                placeholder="Select your roles",
                min_values=0,
                max_values=2,
                options=[
                    discord.SelectOption(label="@LFG", value="LFG"),
                    discord.SelectOption(label="@LFG Beginner", value="LFG Beginner")
                ],
                custom_id="role_select"
            )
        elif(role_type == "Faction"):
            options = [discord.SelectOption(label=name, value=key) for key, name in self.role_map.items() if key not in ["LFG", "LFG Beginner"]]
            @discord.ui.select(
                placeholder="Select your factions",
                min_values=0,
                max_values=27,
                options=options,
                custom_id="faction_select"
            )
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

@discord.app_commands.default_permissions(administrator=True)
class RoleCommands(app_commands.Group):
    @app_commands.command(name="roles", description="Send the role selection menu")
    async def roles(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Role Selection",
            description="Choose your roles below."
        )
        await interaction.response.send_message(embed=embed, view=RoleView())

class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.add_command(RoleCommands())
        await self.tree.sync()

    async def on_ready(self):
        self.add_view(RoleView())
        print(f"Bot online: {self.user}")

bot = Bot()
bot.run(os.getenv("DISCORD_TOKEN"))
