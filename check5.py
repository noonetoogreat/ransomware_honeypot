import volatility.conf as conf
import volatility.registry as registry
registry.PluginImporter()
config = conf.ConfObject()
import volatility.commands as commands
import volatility.addrspace as addrspace
registry.register_global_options(config, commands.Command)
registry.register_global_options(config, addrspace.BaseAddressSpace)
config.parse_options()
config.PROFILE="Win7SP0x86"
config.LOCATION = "file:///media/memory/private/image.dmp"
import volatility.plugins.taskmods as taskmods
p = taskmods.PSList(config)
for process in p.calculate():
	print process