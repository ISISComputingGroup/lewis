from lewis.core import approaches
from lewis.core.statemachine import State

# Would rather this were in device but causes Lewis to fail
MAX_TEMPERATURE = 1


def output_current_state(device, state_name):
    print(
        "{0}: Freq {1:.2f}, Phase {2:.2f}, Error {3:.2f}, Temperature {4:.2f}".format(
            state_name.upper(),
            device.get_true_frequency(),
            device.get_true_phase_delay(),
            device.get_true_phase_error(),
            device.get_temperature(),
        )
    )


class DefaultInitState(State):
    pass


class DefaultStoppedState(State):
    def in_state(self, dt):
        device = self._context
        output_current_state(self._context, "stopped")
        device.set_true_frequency(approaches.linear(device.get_true_frequency(), 0, 1, dt))
        device.set_temperature(approaches.linear(device.get_temperature(), 0, 0.1, dt))
        device.set_true_phase_delay(approaches.linear(device.get_true_phase_delay(), 0, 1, dt))


class DefaultStartedState(State):
    def in_state(self, dt):
        device = self._context
        output_current_state(self._context, "started")
        device.set_true_frequency(
            approaches.linear(device.get_true_frequency(), device.get_demanded_frequency(), 1, dt)
        )
        equilibrium_frequency_temperature = (
            2 * MAX_TEMPERATURE * device.get_true_frequency() / device.get_system_frequency()
        )
        device.set_temperature(
            approaches.linear(
                device.get_temperature(),
                equilibrium_frequency_temperature,
                device.get_true_frequency() * 0.001,
                dt,
            )
        )
        device.set_true_phase_delay(
            approaches.linear(
                device.get_true_phase_delay(), device.get_demanded_phase_delay(), 1, dt
            )
        )
