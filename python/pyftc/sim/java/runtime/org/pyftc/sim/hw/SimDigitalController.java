package org.pyftc.sim.hw;

import com.qualcomm.robotcore.hardware.DigitalChannel;
import com.qualcomm.robotcore.hardware.DigitalChannelController;
import com.qualcomm.robotcore.util.LastKnown;
import com.qualcomm.robotcore.util.SerialNumber;

import org.pyftc.sim.OpModeHost;

/**
 * Port of the FTC SDK 11.2.0 LynxDigitalChannelController. Inputs read the
 * simulated pin (idle high; the scene's touch sensors and limit switches pull
 * it low, since REV's are active-low). Outputs remember the written state.
 */
public final class SimDigitalController implements DigitalChannelController {
    public static final int apiPinFirst = 0;
    public static final int apiPinLast = 7;

    private final Hub hub;

    private static final class PinProperties {
        LastKnown<DigitalChannel.Mode> lastKnownMode = new LastKnown<DigitalChannel.Mode>();
        LastKnown<Boolean> lastKnownState = new LastKnown<Boolean>();
    }

    private final PinProperties[] pins = new PinProperties[8];

    SimDigitalController(Hub hub) {
        this.hub = hub;
        for (int i = 0; i < 8; i++) pins[i] = new PinProperties();
    }

    public void forgetLastKnown() {
        for (PinProperties pin : pins) {
            pin.lastKnownMode.invalidate();
            pin.lastKnownState.invalidate();
        }
    }

    @Override public SerialNumber getSerialNumber() {
        return SerialNumber.createFake();
    }

    @Override public synchronized DigitalChannel.Mode getDigitalChannelMode(int pin) {
        validatePin(pin); pin -= apiPinFirst;
        DigitalChannel.Mode result = pins[pin].lastKnownMode.getValue();
        if (result != null) return result;
        try {
            hub.command();
            result = hub.digitalMode[pin];
            pins[pin].lastKnownMode.setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return DigitalChannel.Mode.INPUT;
    }

    @Override public synchronized void setDigitalChannelMode(int pin, DigitalChannel.Mode mode) {
        DigitalChannel.Mode existingMode = getDigitalChannelMode(pin);
        validatePin(pin); pin -= apiPinFirst;
        internalSetDigitalChannelMode(pin, mode);
        if (existingMode == DigitalChannel.Mode.INPUT && mode == DigitalChannel.Mode.OUTPUT) {
            pins[pin].lastKnownState.setValue(false);
        }
    }

    @Override @Deprecated public void setDigitalChannelMode(int pin, Mode mode) {
        setDigitalChannelMode(pin, mode.migrate());
    }

    private void internalSetDigitalChannelMode(int pinZ, DigitalChannel.Mode mode) {
        try {
            hub.command();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            pins[pinZ].lastKnownMode.invalidate();
            return;
        }
        hub.digitalMode[pinZ] = mode;
        pins[pinZ].lastKnownMode.setValue(mode);
    }

    @Override public synchronized boolean getDigitalChannelState(int pin) {
        DigitalChannel.Mode mode = getDigitalChannelMode(pin);
        validatePin(pin); pin -= apiPinFirst;
        if (mode == DigitalChannel.Mode.OUTPUT) {
            return pins[pin].lastKnownState.getNonTimedValue();
        }
        try {
            hub.command();
            boolean result = hub.digitalInput[pin];
            pins[pin].lastKnownState.setValue(result);
            return result;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return false;
    }

    @Override public synchronized void setDigitalChannelState(int pin, boolean state) {
        DigitalChannel.Mode mode = getDigitalChannelMode(pin);
        validatePin(pin); pin -= apiPinFirst;
        if (mode == DigitalChannel.Mode.OUTPUT) {
            try {
                hub.command();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                pins[pin].lastKnownState.invalidate();
                return;
            }
            hub.digitalOutput[pin] = state;
            pins[pin].lastKnownState.setValue(state);
            OpModeHost.recordCommand(hub.name + " digital " + pin, "setState", state);
        }
    }

    private void validatePin(int pin) {
        if (pin < apiPinFirst || pin > apiPinLast) {
            throw new IllegalArgumentException(String.format("pin %d is invalid; valid pins are %d..%d", pin, apiPinFirst, apiPinLast));
        }
    }

    @Override public Manufacturer getManufacturer() { return Manufacturer.Lynx; }
    @Override public String getDeviceName() { return "Expansion Hub Digital Channel Controller"; }
    @Override public String getConnectionInfo() { return hub.connectionInfo(); }
    @Override public int getVersion() { return 1; }
    @Override public void resetDeviceConfigurationForOpMode() { }
    @Override public void close() { }
}
