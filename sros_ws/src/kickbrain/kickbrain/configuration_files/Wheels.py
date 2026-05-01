from .Configuration import Configuration

from geometry_msgs.msg import Twist

class Wheels(Configuration):

    #TODO: Correct these lists based on actual board location indexing
    X_CONFIG = [0x01, 0x02, 0x01, 0x02]
    O_CONFIG = [0x02, 0x01, 0x02, 0x01]

    def __init__(self, node, active_paths, device_ids):

        super().__init__(node, active_paths, device_ids)

        self.jacobian = None
        self.detect_configuration()

        if self.jacobian:
            self.inertia = self.compute_inertia_matrix()

        self.control_gains = {'P':None, 'I':None, 'D':None} #TODO: Tune control gains for each configuration, and implement control law in fetch_commands
        self.error_integral = 0
        self.error_deriv = 0
        self.prev_error = np.array([0] * 6)

    def detect_configuration(self):

        #Compare the device_ids at indices where active_paths is true to known configurations
        devices = [device for device, active in zip(self.device_ids, self.active_paths) if active]

        if devices == self.X_CONFIG:
            self.jacobian = self.X_Jacobian()
        elif devices == self.O_CONFIG:
            self.jacobian = self.O_Jacobian()
        else:
            self.node.get_logger().warn(f"Unrecognized wheel configuration: {devices}, unable to set Jacobian")

    def fetch_commands(self, vel_cmd: Twist, feedback) -> list:

        if not self.jacobian:
            self.node.get_logger().warn("Jacobian not set, cannot compute commands")
            return [0] * 12  # Safe zero command

        #Map velocity command and feedback to a 6x1 array, compute the difference
        cmd_vel_array = self.vel_to_array(vel_cmd)
        feedback_array = self.vel_to_array(self.compute_received(feedback))
        vel_error = cmd_vel_array - feedback_array
        self.error_integral += vel_error * self.node.timer_period
        self.error_derivative = (vel_error - self.prev_error) / self.node.timer_period
        self.prev_error = vel_error

        #TODO: Add PID controller, inertia jacobian, and J transpose control
        raw_control_signal = np.array([0] * 3) #Placeholder for control signal, to be computed from error and control gains
        if self.control_gains['P']:
            raw_control_signal += self.control_gains['P'] @ vel_error
        if self.control_gains['I']:
            raw_control_signal += self.control_gains['I'] @ self.error_integral
        if self.control_gains['D']:
            raw_control_signal += self.control_gains['D'] @ self.error_deriv

        control_signal = self.jacobian.T @ self.inertia @ raw_control_signal

        #TODO: Need to map control signal to correct wheel data indices
         
        return control_signal.tolist()

    def compute_received(self, device_data) -> Twist:

        if not self.jacobian:
            self.node.get_logger().warn("Jacobian not set, cannot compute velocity")
            return Twist()

        #Take the data from the bus and build an array. Multiply this array by the Jacobian to
        #reconstruct the center of mass velocity of the bot
        wheel_speeds = np.array([data for data, active in zip(device_data, self.active_paths) if active])
        vel_array = self.jacobian @ wheel_speeds #Should be 3x1

        #TODO: Optional sensor fusion with IMU for orientation

        # Set the dictionary to convert to twist (manual is easiest)
        # Assumption: always on level ground
        return_dict = {'linear':[vel_array[0], vel_array[1], 0.0], 'angular':[0.0, 0.0, vel_array[2]]}

        return self.dict_to_twist(return_dict)

    def X_Jacobian(self):
        raise NotImplementedError

    def O_Jacobian(self):
        raise NotImplementedError

    def vel_to_array(self, vel: Twist) -> np.ndarray:

        return np.array([vel.linear.x, vel.linear.y, vel.angular.z])

    def compute_inertia_matrix(self, motor_inertias: list = [9.1818e-6]*4) -> np.ndarray:
        #Compute the inertia Jacobian based on the current configuration and motor inertias, to be used in control loop
        inertia_motor_space = np.diag(motor_inertias)
        try:
            return np.linalg.pinv(self.jacobian) @ inertia_motor_space @ np.linalg.pinv(self.jacobian.T)
        except np.linalg.LinAlgError:
            self.node.get_logger().error("Jacobian is singular, cannot compute inertia Jacobian")
            return np.eye(6) #Fallback to identity, which is not ideal but prevents total failure of control loop
        