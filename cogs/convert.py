import discord
from discord.ext import commands

from data import data
from helpers import *
import settings
import re


class Convert(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.tempwords = ['f','fahrenheit','c','celsius']
		self.long_lenwords_m = ['km','kilometer','kilometers','kilometre','kilometres','m','meter','meters','metre','metres']
		self.long_lenwords_i = ['mi','mile','miles','yd','yard','yards']
		self.short_lenwords_m = ['cm','centimeter','centimeters','m','meter','meters','metre','metres']
		self.short_lenwords_i = ['in','inch','inches','ft','feet']
		self.meterwords = ['m','meter','meters','metre','metres']
		self.weightwords = ['kg','kilogram','kilograms','kilogramme','kilogrammes','kilo','kilos','lb','pound','pounds']

	@commands.command(help="Convert units between freedom and inferior\n\
							Does temperature (°C,°F,°K), length (mi,km,m), and weight (lb,kg)\n\
							Note: commas cannot be used to indicate decimals", 
					  aliases=['c'],
					  usage="<number> <unit> [to <unit>]")
	async def convert(self, ctx, *args):
		args = self.reformat_args(args)
		err, resp = self.errors(args)
		if err:
			await ctx.send(resp)
			return

		unit = args[1]
		num = float(args[0])
		msg = ''

		if unit in self.tempwords:
			msg,desc = self.temperature(args)
		elif unit in self.weightwords:
			msg,desc = self.weight(args)
		elif 'to' in args:
			msg,desc = self.len_specific(args)
		elif unit in self.meterwords:
			if num > 10:
				msg,desc = self.long_len(args)
			else:
				msg,desc = self.short_len(args)
		elif (unit in self.long_lenwords_m) or (unit in self.long_lenwords_i):
			msg,desc = self.long_len(args)
		elif (unit in self.short_lenwords_m) or (unit in self.short_lenwords_i):
			msg,desc = self.short_len(args)
		else:
			msg = 'I don\'t know what that unit is :('
			desc = 'Temperature: F, C\nLength: cm, m, km, in, ft, yd, mi\nWeight: kg, lb'

		emb = discord.Embed(description=desc,color=settings.CONVERT_COLOR)
		await ctx.send(msg,embed=emb)

	def temperature(self, args):
		unit = args[1]
		num = float(args[0].replace(',',''))
		desc = ' '.join(args[:2]) + ' is: '
		if unit == 'f' or unit == 'fahrenheit':
			desc += '**{:.1f}°C**'.format((num-32)/1.8)
		else:
			desc += '**{:.0f}°F**'.format(num*1.8+32)
		return('',desc)

	def long_len(self, args):
		unit = args[1]
		num = float(args[0].replace(',',''))
		msg = ' '.join(args[:2]) + ' is:'

		# kilometers
		if unit in self.long_lenwords_m[:5]:
			desc = '• {:.1f} mi\n• {:.0f} yd'.format(num*0.6213712,num*1093.613)
		# meters
		elif unit in self.meterwords:
			desc = '• {:.1f} mi\n• {:.0f} yd'.format(num*0.0006213712,num*1.093613)
		# miles
		elif unit in self.long_lenwords_i[:3]:
			desc = '• {:.1f} km\n• {:.0f} m\n• {:.0f} yd'.format(num*1.609344,num*1609.344,num*1760)
		# yards
		elif unit in self.long_lenwords_i[3:]:
			desc = '• {:.1f} km\n• {:.0f} m\n• {:.0f} mi'.format(num*0.0009144,num*0.9144,num*0.0005681818)

		return(msg,desc)


	def short_len(self, args):
		unit = args[1]
		num = float(args[0].replace(',',''))
		msg = ' '.join(args[:2]) + ' is:'

		# centimeters
		if unit in self.short_lenwords_m[:3]:
			desc = '• {:.1f} in\n• {:.2f} ft'.format(num*0.3937008,num*0.0328084)
		# meters
		elif unit in self.meterwords:
			desc = '• {:.0f} in\n• {:.1f} ft'.format(num*39.37008,num*3.28084)
		# inches
		elif unit in self.short_lenwords_i[:3]:
			desc = '• {:.1f} cm\n• {:.2f} m\n• {:.2f} ft'.format(num*2.54,num*0.0254,num*0.08333333)
		# feet
		elif unit in self.short_lenwords_i[3:]:
			desc = '• {:.0f} cm\n• {:.2f} m\n• {:.0f} in'.format(num*30.48,num*0.3048,num*12)

		return(msg,desc)

	def len_specific(self, args):
		unit = args[1]
		num = float(args[0].replace(',',''))
		newunit = args[3]
		desc = ' '.join(args[:2]) + ' is: '
		msg = ''

		# kilometers
		if unit in self.long_lenwords_m[:5]:
			# to kilometers
			if newunit in self.long_lenwords_m[:5]:
				desc += '**{} km**'.format(str(num))
			# to meters
			elif newunit in self.meterwords:
				desc += '**{:.0f} m**'.format(num*1000)
			# to miles
			elif newunit in self.long_lenwords_i[:3]:
				desc += '**{:.1f} mi**'.format(num*0.6213712)
			# to yards
			elif newunit in self.long_lenwords_i[3:]:
				desc += '**{:.1f} yd**'.format(num*1093.613)
			# to centimeters
			elif newunit in self.short_lenwords_m[:3]:
				desc += '**{:.0f} cm**'.format(num*100000)
			# to inches
			elif newunit in self.short_lenwords_i[:3]:
				desc += '**{:.0f} in**'.format(num*39370.08)
			# to feet
			elif newunit in self.short_lenwords_i[3:]:
				desc += '**{:.0f} ft**'.format(num*3280.84)
		# meters
		elif unit in self.meterwords:
			# to kilometers
			if newunit in self.long_lenwords_m[:5]:
				desc += '**{:.5f} km**'.format(num*0.001)
			# to meters
			elif newunit in self.meterwords:
				desc += '**{} m**'.format(str(num))
			# to miles
			elif newunit in self.long_lenwords_i[:3]:
				desc += '**{:.5f} mi**'.format(num*0.0006213712)
			# to yards
			elif newunit in self.long_lenwords_i[3:]:
				desc += '**{:.5f} yd**'.format(num*1.093613)
			# to centimeters
			elif newunit in self.short_lenwords_m[:3]:
				desc += '**{:.0f} cm**'.format(num*100)
			# to inches
			elif newunit in self.short_lenwords_i[:3]:
				desc += '**{:.0f} in**'.format(num*39.37008)
			# to feet
			elif newunit in self.short_lenwords_i[3:]:
				desc += '**{:.1f} ft**'.format(num*3.28084)
		# miles
		elif unit in self.long_lenwords_i[:3]:
			# to kilometers
			if newunit in self.long_lenwords_m[:5]:
				desc += '**{:.1f} km**'.format(num*1.609344)
			# to meters
			elif newunit in self.meterwords:
				desc += '**{:.0f} m**'.format(num*1609.344)
			# to miles
			elif newunit in self.long_lenwords_i[:3]:
				desc += '**{} mi**'.format(str(num))
			# to yards
			elif newunit in self.long_lenwords_i[3:]:
				desc += '**{:.0f} yd**'.format(num*1760)
			# to centimeters
			elif newunit in self.short_lenwords_m[:3]:
				desc += '**{:.0f} cm**'.format(num*160934.4)
			# to inches
			elif newunit in self.short_lenwords_i[:3]:
				desc += '**{:.0f} in**'.format(num*63360)
			# to feet
			elif newunit in self.short_lenwords_i[3:]:
				desc += '**{:.0f} ft**'.format(num*5280)
		# yards
		elif unit in self.long_lenwords_i[3:]:
			# to kilometers
			if newunit in self.long_lenwords_m[:5]:
				desc += '**{:.5f} km**'.format(num*0.0009144)
			# to meters
			elif newunit in self.meterwords:
				desc += '**{:.1f} m**'.format(num*0.9144)
			# to miles
			elif newunit in self.long_lenwords_i[:3]:
				desc += '**{:.5f} mi**'.format(num*0.0005681818)
			# to yards
			elif newunit in self.long_lenwords_i[3:]:
				desc += '**{} yd**'.format(str(num))
			# to centimeters
			elif newunit in self.short_lenwords_m[:3]:
				desc += '**{:.0f} cm**'.format(num*91.44)
			# to inches
			elif newunit in self.short_lenwords_i[:3]:
				desc += '**{:.0f} in**'.format(num*36)
			# to feet
			elif newunit in self.short_lenwords_i[3:]:
				desc += '**{:.0f} ft**'.format(num*3)
		# centimeters
		elif unit in self.short_lenwords_m[:3]:
			# to kilometers
			if newunit in self.long_lenwords_m[:5]:
				desc += '**{:.5f} km**'.format(num*0.00001)
			# to meters
			elif newunit in self.meterwords:
				desc += '**{:.5f} m**'.format(num*0.01)
			# to miles
			elif newunit in self.long_lenwords_i[:3]:
				desc += '**{:.5f} mi**'.format(num*0.000006213712)
			# to yards
			elif newunit in self.long_lenwords_i[3:]:
				desc += '**{:.5f} yd**'.format(num*0.01093613)
			# to centimeters
			elif newunit in self.short_lenwords_m[:3]:
				desc += '**{} cm**'.format(str(num))
			# to inches
			elif newunit in self.short_lenwords_i[:3]:
				desc += '**{:.1f} in**'.format(num*0.3937008)
			# to feet
			elif newunit in self.short_lenwords_i[3:]:
				desc += '**{:.1f} ft**'.format(num*0.0328084)
		# inches
		elif unit in self.short_lenwords_i[:3]:
			# to kilometers
			if newunit in self.long_lenwords_m[:5]:
				desc += '**{:.5f} km**'.format(num*0.0000254)
			# to meters
			elif newunit in self.meterwords:
				desc += '**{:.2f} m**'.format(num*0.0254)
			# to miles
			elif newunit in self.long_lenwords_i[:3]:
				desc += '**{:.5f} mi**'.format(num*0.00001578283)
			# to yards
			elif newunit in self.long_lenwords_i[3:]:
				desc += '**{:.2f} yd**'.format(num*0.02777778)
			# to centimeters
			elif newunit in self.short_lenwords_m[:3]:
				desc += '**{:.1f} cm**'.format(num*2.54)
			# to inches
			elif newunit in self.short_lenwords_i[:3]:
				desc += '**{} in**'.format(str(num))
			# to feet
			elif newunit in self.short_lenwords_i[3:]:
				desc += '**{:.1f} ft**'.format(num*0.08333333)
		# feet
		elif unit in self.short_lenwords_i[3:]:
			# to kilometers
			if newunit in self.long_lenwords_m[:5]:
				desc += '**{:.5f} km**'.format(num*0.0003048)
			# to meters
			elif newunit in self.meterwords:
				desc += '**{:.1f} m**'.format(num*0.3048)
			# to miles
			elif newunit in self.long_lenwords_i[:3]:
				desc += '**{:.5f} mi**'.format(num*0.0001893939)
			# to yards
			elif newunit in self.long_lenwords_i[3:]:
				desc += '**{:.1f} yd**'.format(num*0.3333333)
			# to centimeters
			elif newunit in self.short_lenwords_m[:3]:
				desc += '**{:.0f} cm**'.format(num*30.48)
			# to inches
			elif newunit in self.short_lenwords_i[:3]:
				desc += '**{:.0f} in**'.format(num*12)
			# to feet
			elif newunit in self.short_lenwords_i[3:]:
				desc += '**{} ft**'.format(str(num))
		else:
			msg = 'I don\'t know what that unit is :('
			desc = 'Temperature: F, C\nLength: cm, m, km, in, ft, yd, mi\nWeight: kg, lb'

		return(msg,desc)

	def weight(self, args):
		unit = args[1]
		num = float(args[0].replace(',',''))
		desc = ' '.join(args[:2]) + ' is: '
		# kg to lb
		if unit in self.weightwords[:7]:
			desc += '**{:.1f} lb**'.format(num*2.2046226218488)
		# lb to kg
		else:
			desc += '**{:.1f} kg**'.format(num*0.45359237)
		return('',desc)


	def errors(self, args):
		if len(args)<2:
			return(True,'I don\'t know how to convert that 🤷‍♀️')

		# Check number is there	
		try:
			num = float(args[0].replace(',',''))
		except:
			return(True,'I can\'t figure out what number that is :(\n')

		if len(args) > 3:
			newunit = args[3].lower()
			if (newunit not in self.long_lenwords_m) and (newunit not in self.long_lenwords_i):
				if (newunit not in self.short_lenwords_m) and (newunit not in self.short_lenwords_i):
					if (newunit not in self.tempwords) and (newunit not in self.weightwords):
						return(True, 'I don\'t know what that second unit is')

		return(False,'')

	def reformat_args(self, args):
		newargs = [x.lower() for x in args]
		newargs[0] = newargs[0].replace(',','')
		try:
			test = float(newargs[0])
		except:
			numbre = re.compile('-?\d*\.?\d*')
			numb = numbre.match(newargs[0]).group()
			unit = newargs[0][len(numb):]

			newargs[0] = numb
			newargs.insert(1, unit)

		return newargs




def setup(bot):
	bot.add_cog(Convert(bot))


