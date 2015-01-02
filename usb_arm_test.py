import usb_arm
import unittest
import time

def time_msec():
    return round(time.time() * 1000.0)

class StubUsb:
    def __init__(self):
        self.ctrl_commands=[]
    
    def ctrl_transfer(self, reqType, req, value, idx, data=None, length=None):
        self.ctrl_commands.append((data, time_msec()))

    def get_last_ctrl_command(self):
        return self.ctrl_commands[len(self.ctrl_commands)-1]

    def get_ctrl_commands(self):
        return self.ctrl_commands

    def reset(self):
        self.ctrl_commands = []
        
class TestableArm(usb_arm.Arm):
    def __init__(self):
        self.dev = StubUsb()

    def assert_ctrl_cmds(self, commands):
        ret = True
        for idx in range(len(self.dev.get_ctrl_commands())):
            cmd, time = self.dev.get_ctrl_commands()[idx]
            ret = ret and cmd == commands[idx]
        return ret

    def get_ctrl_cmd(self, idx):
        return self.dev.get_ctrl_commands()[idx]

    def get_ctrl_cmds(self):
        return self.dev.get_ctrl_commands()

    def get_ctrl_cmd_list(self):
        return list(map(lambda cmd: cmd[0], self.dev.get_ctrl_commands()))

class UsbArmTest(unittest.TestCase):

    def setUp(self):
        self.arm = TestableArm()

    def test_move_includes_correct_verb(self):
        self.arm.move(usb_arm.LedOn)
        cmd, time = self.arm.get_ctrl_cmd(0)
        self.assertEqual(usb_arm.LedOn, cmd)

    def test_move_adds_stop_verb(self):
        self.arm.move(usb_arm.ShoulderDown)
        self.assertEqual([usb_arm.ShoulderDown, usb_arm.Stop], self.arm.get_ctrl_cmd_list())

    def test_default_move_time(self):
        self.arm.move(usb_arm.ElbowUp)
        cmd0, time0 = self.arm.get_ctrl_cmd(0)
        cmd1, time1 = self.arm.get_ctrl_cmd(1)
        self.assertIn(time1 - time0, range(990, 1010))

    def test_specific_move_time(self):
        self.arm.move(usb_arm.ElbowUp, 2)
        cmd0, time0 = self.arm.get_ctrl_cmd(0)
        cmd1, time1 = self.arm.get_ctrl_cmd(1)
        self.assertIn(time1 - time0, range(1090, 2010))

if __name__ == '__main__':
    unittest.main()
    
