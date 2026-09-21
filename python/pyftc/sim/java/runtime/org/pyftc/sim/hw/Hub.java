package org.pyftc.sim.hw;

import com.qualcomm.robotcore.hardware.DigitalChannel;

import org.pyftc.sim.Constants;
import org.pyftc.sim.OpModeHost;
import org.pyftc.sim.SimClock;

/**
 * One simulated REV hub (Control Hub or Expansion Hub): four motor ports, six
 * servo ports, eight digital channels, four analog inputs, and the cost of a
 * Lynx command on its link.
 */
public final class Hub {
    public final String name;
    public final int address;
    public final boolean controlHub;
    public final long commandNs;
    public final long i2cNs;

    public final MotorChannel[] motors = new MotorChannel[4];
    public final ServoChannel[] servos = new ServoChannel[6];
    public final boolean[] digitalInput = new boolean[8];
    public final boolean[] digitalOutput = new boolean[8];
    public final DigitalChannel.Mode[] digitalMode = new DigitalChannel.Mode[8];
    public final double[] analogVolts = new double[4];

    public SimDcMotorController motorController;
    public SimServoController servoController;
    public SimDigitalController digitalController;
    public SimAnalogController analogController;
    public SimVoltageSensor voltageSensor;

    public Hub(String name, int address, boolean controlHub) {
        this.name = name;
        this.address = address;
        this.controlHub = controlHub;
        this.commandNs = (long) (Constants.num(controlHub ? "lynx.commandMsControlHub" : "lynx.commandMsExpansionHub") * 1e6);
        this.i2cNs = (long) (Constants.num("lynx.i2cMs") * 1e6);
        for (int i = 0; i < motors.length; i++) motors[i] = new MotorChannel(i);
        for (int i = 0; i < servos.length; i++) servos[i] = new ServoChannel(i);
        for (int i = 0; i < 8; i++) {
            // Digital inputs idle high (the hub's pull-ups); REV's active-low sensors pull them low.
            digitalInput[i] = true;
            digitalMode[i] = DigitalChannel.Mode.INPUT;
        }
        motorController = new SimDcMotorController(this);
        servoController = new SimServoController(this);
        digitalController = new SimDigitalController(this);
        analogController = new SimAnalogController(this);
        voltageSensor = new SimVoltageSensor(this);
    }

    /**
     * What sending one Lynx command costs the calling thread, with the Lynx
     * failure modes that matter to user code: after STOP the OpMode thread is
     * interrupted and its commands are dropped (InterruptedException, which the
     * SDK swallows after re-setting the interrupt flag); once the stop timeout
     * has passed, commands throw ForceStopException, as the RC does to kill a
     * stuck OpMode.
     */
    public void transact(long ns) throws InterruptedException {
        if (SimClock.isUserThread()) {
            OpModeHost.checkForceStop();
            if (Thread.interrupted()) throw new InterruptedException();
        }
        SimClock.charge(ns);
    }

    public void command() throws InterruptedException {
        transact(commandNs);
    }

    public void step(double dt, double batteryVolts) {
        for (MotorChannel m : motors) m.step(dt, batteryVolts);
        for (ServoChannel s : servos) s.step(dt);
    }

    public String connectionInfo() {
        return (controlHub ? "Control Hub" : "Expansion Hub") + " (sim) address " + address;
    }
}
