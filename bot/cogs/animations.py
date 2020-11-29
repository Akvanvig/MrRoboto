import asyncio

from discord.ext import commands

#
# CONSTANTS
#

UPDATE_TICK = 0.3

#
# CLASSES
#

class Animations(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def _animate(self, ctx, animation, *, num_loop = 1):
        message = await ctx.send(animation[0])
        for i in range(num_loop):
            for frame in animation:
                await message.edit(content=frame)
                await asyncio.sleep(UPDATE_TICK)

    #
    # COMMANDS
    #

    @commands.command()
    async def howdy(self, ctx):
        animation = [":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :eggplant:\n               :zap:8==:punch:D:sweat_drops:\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:sweat_drops:\n           :carrot:  :eggplant:                  :sweat_drops:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::nose:\n               :oil:  :nose:\n               :zap:8:punch:==D:sweat_drops:\n           :carrot:  :eggplant:                  :sweat_drops:\n           :boot:     :boot:                   :sweat_drops:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:sweat_drops:\n           :carrot:  :eggplant:                  :sweat_drops:\n           :boot:     :boot:"]
        await self._animate(ctx, animation, num_loop = 20)

    @commands.command()
    async def howdysplurt(self, ctx):
        animation = [":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :eggplant:\n               :zap:8==:punch:D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::nose:\n               :oil:  :nose:\n               :zap:8:punch:==D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :eggplant:\n               :zap:8==:punch:D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::nose:\n               :oil:  :nose:\n               :zap:8:punch:==D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:ocean:\n           :carrot:  :eggplant:                  :ocean:\n           :boot:     :boot:                    :ocean:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:ocean::ocean::ocean::ocean::ocean:\n           :carrot:  :eggplant:                  :ocean::ocean::ocean::ocean::ocean:\n           :boot:     :boot:                    :ocean::ocean::ocean::ocean::ocean:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :carrot:  :eggplant:                  :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :boot:     :boot:                    :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :carrot:  :eggplant:                  :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :boot:     :boot:                    :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:",":thumbsup:          :cowboy:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :carrot:  :eggplant:                  :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :boot:     :boot:                    :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:",":thumbsup:          :frowning:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:=D:ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :carrot:  :eggplant:                  :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:\n           :boot:     :boot:                    :ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean::ocean:",":thumbsup:          :frowning:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch::boom:=D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :frowning:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:           =D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :frowning:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:           :red_circle:=D\n           :carrot:  :eggplant:\n           :boot:     :boot:",":thumbsup:          :frowning:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:           :red_circle:\n           :carrot:  :eggplant:                    :red_circle:=D\n           :boot:     :boot:",":thumbsup:          :frowning:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch:           :red_circle:\n           :carrot:  :eggplant:                    :red_circle:\n           :boot:     :boot:                   :red_circle:=D",":thumbsdown:          :sob:\n   :eggplant::zzz::necktie::eggplant:\n               :oil:    :nose:\n               :zap:8=:punch::red_circle:\n           :carrot:  :eggplant:         :red_circle:\n           :boot:     :boot:       :red_circle::red_circle::red_circle:=D"]
        await self._animate(ctx, animation)

#
# SETUP
#

def setup(client):
    client.add_cog(Animations(client))