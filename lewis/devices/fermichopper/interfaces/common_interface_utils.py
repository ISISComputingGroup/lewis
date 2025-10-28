from lewis.utils.command_builder import CmdBuilder

HEX_LEN_2 = "[0-9A-F]{2}"
HEX_LEN_4 = "[0-9A-F]{4}"

COMMANDS = {
    CmdBuilder("get_all_data").escape("#00000").arg(HEX_LEN_2).build(),
    CmdBuilder("execute_command").escape("#1").arg(HEX_LEN_4).arg(HEX_LEN_2).build(),
    CmdBuilder("set_speed").escape("#3").arg(HEX_LEN_4).arg(HEX_LEN_2).build(),
    CmdBuilder("set_delay_highword").escape("#6").arg(HEX_LEN_4).arg(HEX_LEN_2).build(),
    CmdBuilder("set_delay_lowword").escape("#5").arg(HEX_LEN_4).arg(HEX_LEN_2).build(),
    CmdBuilder("set_gate_width").escape("#9").arg(HEX_LEN_4).arg(HEX_LEN_2).build(),
}
