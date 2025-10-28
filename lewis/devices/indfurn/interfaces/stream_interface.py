from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder

from lewis_emulators.indfurn.device import SampleHolderMaterials

SAMPLE_HOLDER_MATERIALS = {
    "aluminium": SampleHolderMaterials.ALUMINIUM,
    "glassy_carbon": SampleHolderMaterials.GLASSY_CARBON,
    "graphite": SampleHolderMaterials.GRAPHITE,
    "quartz": SampleHolderMaterials.QUARTZ,
    "single_crystal_sapphire": SampleHolderMaterials.SINGLE_CRYSTAL_SAPPHIRE,
    "steel": SampleHolderMaterials.STEEL,
    "vanadium": SampleHolderMaterials.VANADIUM,
}


@has_log
class IndfurnStreamInterface(StreamInterface):
    commands = {
        # ID
        CmdBuilder("get_version").escape("?ver").eos().build(),
        CmdBuilder("get_setpoint").escape("?pidSP").eos().build(),
        CmdBuilder("set_setpoint").escape(">pidSP ").float().eos().build(),
        CmdBuilder("get_psu_voltage").escape("?powV").eos().build(),
        CmdBuilder("set_psu_voltage").escape(">powV ").float().eos().build(),
        CmdBuilder("get_psu_current").escape("?powI").eos().build(),
        CmdBuilder("set_psu_current").escape(">powI ").float().eos().build(),
        CmdBuilder("get_output").escape("?pidOUTM").eos().build(),
        CmdBuilder("set_output").escape(">pidOUTM ").float().eos().build(),
        CmdBuilder("get_thermocouple_temperature").escape("?tempTC").eos().build(),
        CmdBuilder("get_thermocouple2_temperature").escape("?tmpTC2").eos().build(),
        CmdBuilder("get_pipe_temperature").escape("?tempP").eos().build(),
        CmdBuilder("get_capacitor_bank_temperature").escape("?tempC").eos().build(),
        CmdBuilder("get_fet_temperature").escape("?tempS").eos().build(),
        CmdBuilder("get_pid_params").escape("?pidTu").eos().build(),
        CmdBuilder("set_pid_params")
        .escape(">pidTu ")
        .float()
        .escape(" ")
        .float()
        .escape(" ")
        .float()
        .eos()
        .build(),
        CmdBuilder("get_sample_time").escape("?pidSt").eos().build(),
        CmdBuilder("set_sample_time").escape(">pidSt ").int().eos().build(),
        CmdBuilder("get_psu_direction").escape("?pidDir").eos().build(),
        CmdBuilder("set_psu_direction").escape(">pidDir ").any().eos().build(),
        CmdBuilder("get_pid_mode").escape("?pidMODE").eos().build(),
        CmdBuilder("set_pid_mode").escape(">pidMODE ").char().eos().build(),
        CmdBuilder("set_psu_remote").escape(">powR").eos().build(),
        CmdBuilder("set_psu_local").escape(">powL").eos().build(),
        CmdBuilder("get_psu_control_mode").escape("?powRL").eos().build(),
        CmdBuilder("set_psu_on").escape(">powON").eos().build(),
        CmdBuilder("set_psu_off").escape(">powOFF").eos().build(),
        CmdBuilder("get_psu_power").escape("?powOnOff").eos().build(),
        CmdBuilder("set_led_on").escape(">ledON").eos().build(),
        CmdBuilder("set_led_off").escape(">ledOFF").eos().build(),
        CmdBuilder("get_led").escape("?ledOnOff").eos().build(),
        CmdBuilder("set_hf_on").escape(">oscON").eos().build(),
        CmdBuilder("set_hf_off").escape(">oscOFF").eos().build(),
        CmdBuilder("get_hf_power").escape("?oscOnOff").eos().build(),
        CmdBuilder("get_pid_limits").escape("?pidOUTL").eos().build(),
        CmdBuilder("set_pid_limits").escape(">pidOUTL ").float().escape(" ").float().eos().build(),
        CmdBuilder("get_psu_overtemp").escape("?alarmh").eos().build(),
        CmdBuilder("get_psu_overvolt").escape("?alarmv").eos().build(),
        CmdBuilder("get_cooling_water_flow_status").escape("?flowSt").eos().build(),
        CmdBuilder("get_cooling_water_flow").escape("?flowCw").eos().build(),
        CmdBuilder("reset_alarms").escape(">ackAlarm").eos().build(),
        CmdBuilder("set_runmode_on").escape(">pidRUN").eos().build(),
        CmdBuilder("set_runmode_off").escape(">pidSTP").eos().build(),
        CmdBuilder("get_runmode").escape("?pidRUN").eos().build(),
        CmdBuilder("get_sample_holder_material").escape("?sHold").eos().build(),
        CmdBuilder("set_sample_holder_material").escape(">sHold ").string().eos().build(),
        CmdBuilder("get_tc_fault").escape("?faultTC").eos().build(),
        CmdBuilder("get_tc2_fault").escape("?fltTC2").eos().build(),
    }

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(
            request, error.__class__.__name__, error
        )
        print(err_string)
        self.log.error(err_string)
        return "<Unsupported command"

    def get_pid_mode(self):
        return "<pmode {}".format("a" if self.device.pid_mode_automatic else "m")

    def set_pid_mode(self, pid_mode):
        if pid_mode == "a":
            self.device.pid_mode_automatic = True
            return "<ack"
        elif pid_mode == "m":
            self.device.pid_mode_automatic = False
            return "<ack"
        else:
            return "<nak"

    def get_version(self):
        name = "EMULATED FURNACE"
        return "<{name}{terminator}<{name}".format(name=name, terminator="\r\n")

    def get_setpoint(self):
        return "<pidsp {:.2f}".format(self.device.setpoint)

    def set_setpoint(self, sp):
        self.device.setpoint = sp
        return "<ack"

    def get_psu_voltage(self):
        return "<powv {:.2f}".format(self.device.psu_voltage)

    def set_psu_voltage(self, voltage):
        self.device.psu_voltage = voltage
        return "<ack"

    def get_psu_current(self):
        return "<powa {:.2f}".format(self.device.psu_current)

    def set_psu_current(self, current):
        self.device.psu_current = current
        return "<ack"

    def get_output(self):
        return "<pidoutm {:.2f}".format(self.device.output)

    def set_output(self, output):
        self.device.output = output
        return "<ack"

    def get_thermocouple_temperature(self):
        return "<temptc {:.2f}".format(self.device.setpoint)

    def get_thermocouple2_temperature(self):
        return "<temptc2 {:.2f}".format(self.device.setpoint)

    def get_pipe_temperature(self):
        return "<tempp {:.2f}".format(self.device.pipe_temperature)

    def get_capacitor_bank_temperature(self):
        return "<tempc {:.2f}".format(self.device.capacitor_bank_temperature)

    def get_fet_temperature(self):
        return "<temps {:.2f}".format(self.device.fet_temperature)

    def get_pid_params(self):
        return "<pidtu {:.2f} {:.2f} {:.2f}".format(self.device.p, self.device.i, self.device.d)

    def set_pid_params(self, p, i, d):
        self.device.p = p
        self.device.i = i
        self.device.d = d
        return "<ack"

    def get_pid_limits(self):
        return "<PID out limit min max:  {:.2f} {:.2f}".format(
            self.device.pid_lower_limit, self.device.pid_upper_limit
        )

    def set_pid_limits(self, pid_lower_limit, pid_upper_limit):
        self.device.pid_lower_limit = pid_lower_limit
        self.device.pid_upper_limit = pid_upper_limit
        return "<ack"

    def get_sample_time(self):
        return "<pidst {:d}".format(self.device.sample_time)

    def set_sample_time(self, sample_time):
        self.device.sample_time = sample_time
        return "<ack"

    def get_psu_direction(self):
        return "<piddir {}".format("p" if self.device.direction_heating else "n")

    def set_psu_direction(self, direction):
        if direction == "DIR":
            self.device.direction_heating = True
            return "<ack"
        elif direction == "REV":
            self.device.direction_heating = False
            return "<ack"
        else:
            return "<nak"

    def get_psu_overtemp(self):
        return "<{}".format("on" if self.device.psu_overtemp else "off")

    def get_psu_overvolt(self):
        return "<{}".format("on" if self.device.psu_overvolt else "off")

    def get_cooling_water_flow_status(self):
        return "<{}".format("ok" if self.device.is_cooling_water_flow_ok() else "nok")

    def get_cooling_water_flow(self):
        return "<flow {}".format(self.device.cooling_water_flow)

    def reset_alarms(self):
        self.device.psu_overtemp = False
        self.device.psu_overvolt = False
        return "<ack"

    def set_psu_remote(self):
        self.device.remote_mode = True
        return "<ack"

    def set_psu_local(self):
        self.device.remote_mode = False
        return "<ack"

    def set_psu_on(self):
        self.device.power_supply_on = True
        return "<ack"

    def set_psu_off(self):
        self.device.power_supply_on = False
        return "<ack"

    def set_led_on(self):
        self.device.sample_area_led_on = True
        return "<ack"

    def set_led_off(self):
        self.device.sample_area_led_on = False
        return "<ack"

    def set_hf_on(self):
        self.device.hf_on = True
        return "<ack"

    def set_hf_off(self):
        self.device.hf_on = False
        return "<ack"

    def set_runmode_on(self):
        self.device.running = True
        return "<ack"

    def set_runmode_off(self):
        self.device.running = False
        return "<ack"

    def get_runmode(self):
        return "<{}".format("on" if self.device.running else "off")

    def get_psu_control_mode(self):
        return "<{}".format("remote" if self.device.remote_mode else "local")

    def get_psu_power(self):
        return "<{}".format("on" if self.device.power_supply_on else "off")

    def get_led(self):
        return "<{}".format("on" if self.device.sample_area_led_on else "off")

    def get_hf_power(self):
        return "<{}".format("on" if self.device.hf_on else "off")

    def get_sample_holder_material(self):
        for k, v in SAMPLE_HOLDER_MATERIALS.items():
            if v == self.device.sample_holder_material:
                return "<{}".format(k)
        else:
            return "<nak"

    def set_sample_holder_material(self, material):
        try:
            self.device.sample_holder_material = SAMPLE_HOLDER_MATERIALS[material]
            return "<ack"
        except KeyError:
            return "<nak"

    def get_tc_fault(self):
        return "<faulttc {}".format(self.device.thermocouple_1_fault)

    def get_tc2_fault(self):
        return "<faulttc2 {}".format(self.device.thermocouple_2_fault)
