# -*- coding: utf-8 -*-
"""
example on how to plot decoded sensor data from crazyflie
@author: jsschell
"""
import CF_functions as cff
import matplotlib.pyplot as plt
import re
import getopt
import os
import sys

def usage():
    print ('Options:')
    print ('None / default: "log00.txt" should be in the script directory')
    print ('-f /--file_name/--dir_name=  <Path/with/file/name without File Extension or Path/to/Dir >')
    print ('-k /--key_group=  <Key group name(s) as comma separated list>')
    print ('-a /--all  (If true, all available data is plotted)')
    # print ('-v /--vicon=      (If true, vicon data is plotted if available)')
    # print ('-s /--save_name=  <Name for the saved plots> (If added, all used plots are saved to disk with save_name)')
    print ('Example:        python3 analyze_log_data.py -f log06')
    print ('With full path: python3 analyze_log_data.py -f path/to/log_name')

try:
    opts, _ = getopt.getopt(sys.argv[1:], 'f:k:v:s:a', ['file_name=','key_group=','vicon=','save_name=','all'])
except getopt.GetoptError:
    usage()
    sys.exit(2)

log_name = "log00"
multi_log = False

for opt, arg in opts:
    if opt in ('-f', '--file_name', '--dir_name'):
        if os.path.isdir(arg):
            log_list = os.listdir(arg)
            log_dir = arg
            multi_log = True
        elif os.path.isfile(arg):
            log_name = arg
    if opt in ('-a', '--all'): plot_all = True
    elif opt in ('-k', '--key_group'):
        key_to_plot_alone = arg
    else:
        key_to_plot_alone = None
        plot_all = False

if multi_log:
    logDataList = []
    for log_file in log_list:
        logData = cff.decode(os.path.join(log_dir,log_file))
        logDataList.append(logData)
        printed = []
        for data in logDataList:
            keys = ""
            for k, v in data.items():
                keys += k
                if k not in printed:
                    print(k)
                printed.append(k)
else:
    # decode binary log data
    logData = cff.decode(log_name)
    # let's see which keys exists in current data set
    keys = ""
    for k, v in logData.items():
        keys += k
        print(k)

if key_to_plot_alone != None:
    keys = key_to_plot_alone
    print(keys)




# set window background to white
plt.rcParams['figure.facecolor'] = 'w'


# plot functions
"""
key_group           :=
group_label         :=
sub_key_list        :=
sub_key_label_list  ;=
plot_y_label        :=
plot_titl           :=
figure_ID           := Number or String. The ID for plot different logged data in a single Figure
"""
def include_log(key_group,group_label,sub_key_list,sub_key_label_list,plot_y_label,plot_title,figure_ID):
    inStr = ''
    plotsPerFigure = 4
    if re.search(key_group, keys):
        if not plot_all and not key_to_plot_alone:
            inStr = input('plot ' + str(group_label) + ' data? ([Y]es / [n]o): ')
        if ((re.search('^[Yy]', inStr)) or (inStr == '') or plot_all or key_to_plot_alone):
            for sub_key_input in sub_key_list:
                bSubKeyMissing = False
                if (key_group + '.' + sub_key_input) in logData:
                    print(key_group + '.' + sub_key_input + ' vorhanden')
                else:
                    print(key_group + '.' + sub_key_input + ' nicht vorhanden')
                    bSubKeyMissing = True
            if bSubKeyMissing:
                return
            if multi_log:
                (nFigures, nlogsLastFig) = divmod(len(log_list),plotsPerFigure)
                cFigures = 1
                for c, (logDataMulti, log_name_nulti) in enumerate(zip(logDataList, log_list)):
                    if (c % 4) == 0:
                        plt.figure(figure_ID)
                        cFigures += 1
                    (nSubplot, divSubPlots) = divmod(c,plotsPerFigure)
                    plt.subplot(plotsPerFigure,1,divSubPlots+1)
                    if c == 0: plt.title(plot_title)
                    for (sub_key, sub_key_label) in zip(sub_key_list,sub_key_label_list):
                        plt.plot(logDataMulti['tick'], logDataMulti[key_group + '.' + sub_key], '-', label=(sub_key_label + ' ' + str(log_name_nulti)))
                    plt.xlabel('RTOS Ticks')
                    plt.ylabel(plot_y_label)
                    plt.legend(loc=0, ncol=3, borderaxespad=0.)
            else:
                plt.figure(figure_ID)
                for (sub_key, sub_key_label) in zip(sub_key_list,sub_key_label_list):
                    plt.plot(logData['tick'], logData[key_group + '.' + sub_key], '-', label=sub_key_label)
                plt.xlabel('RTOS Ticks')
                plt.ylabel(plot_y_label)
                plt.title(plot_title)
                plt.legend(loc=0, ncol=3, borderaxespad=0.)
    return


# usage of "include new data to log plots" functions
# include_log(logging group name [string],name to ask in console [string],logging group keys [list of strings],
#   logging group key legend labels [list of strings],ylabel [string],title [string]):
#
# IF ONLY ONE LOGGING GROUP KEY USE NON CURLY BRACKETS AROUND THE STRING INPUT !!!
# Example: (['aZimu'])

# figure 1
include_log('vicon','Vicon Position',('x','y','z'),('X','Y','Z'),'Position [m]','Vicon Position',1)
# figure 3
include_log('ctrlMel','Controller Mellinger',('Mx','My'),('Mx','My'),'moments','By Mellinger calculated moments',3)
# figure 4
include_log('ctrlMel','Controller Mellinger',(['cThrust']),(['current thrust']),'current thrust','current thrust from Mellinger Controller',4)
# figure angles
include_log('vicon','Vicon Angles',('pitch','roll'),('pitch actual','roll actual'),'pitch and roll [Deg]','Actual Angles','angles')
include_log('ctrlMel','Controller Mellinger',('pitchd','rolld'),('pitch desired','roll desired'),'pitch and roll [Deg]','Desired Angles','angles')
include_log('kalmanUSC','Estimator Kalman USC',('pitch_eUSC','roll_eUSC'),('pitch estimated','roll estimated'),'pitch and roll [DEG]','Angles','angles')


#include_log('vicon','Vicon Velocity',('v_x','v_y','v_z'),('vX','vY','vZ'),'Velocity [m/s]','Vicon Velocity')
#include_log('vicon','Vicon System Latency',(['dt']),(['dT']),'Time since last Pkg [ms]','Vicon Package Arrival')
#include_log('vicon','Start Flag',(['startFlag']),(['startFlag']),'Time since last Pkg [ms]','startFlag')
#include_log('vicon','FuckYou',(['fuckYou']),(['fuckYou']),'Time since last Pkg [ms]','fuckYou')
# #  Control Data
# include_log('ctrltarget','CTRL Target',('roll','pitch','yaw'),('Roll','Pitch','Yaw'),'Object Rot Angle [°]','Control Target Data')
# include_log('ctrltarget','CTRL Target Data',('emergencyStop','upsideDown'),('Emergency Stop ','Upside Down '),'Triggered? [bool]','Control Target FLAGS')
# include_log('ctrltarget','CTRL Target Data',(['aZimu']),(['Acc Z from IMU']),'Z Acc [m/s²]','Control Target Z Acc')
# # IMU Data
# include_log('gyro','Gyroscope',('x','y','z'),('X','Y','Z'),'Position [m]','Gyroscope Rotation')
# include_log('acc','Acceleration IMU',('x','y','z'),('a_X','a_Y','a_Z'),'Acceleration [m/s²]','Acceleration from IMU')
# include_log('mag','Magnetometer IMU',('x','y','z'),('g_X','g_Y','g_Z'),'Magnetometer [?]','Magnetometer from IMU')
# include_log('baro','Pressure IMU',('pressure'),('Pressure'),'Pressure [bar?]','Pressure from IMU')
# # Stabilizer
# include_log('stabilizer','Stabilizer',('roll','pitch','yaw'),('Roll','Pitch','Yaw'),'Object Rot Angle [°]','Stabilizer Values')
# include_log('stabilizer','Stabilizer Thrust',(['thrust']),(['Thrust']),'Thrust [?]','Stabilizer only Thrust')
# # Radio
# include_log('radio','Radio Data',(['rssi']),(['RSSI']),'Signal Strength [?]','Radio Signal Strength')
# # Motor data
# include_log('motor','Motor Values',('m1','m2','m3','m4'),('Motor 1','Motor 2','Motor 3','Motor 4'),'Motor Thrust [?]','Motor Thrusts')
# include_log('pwm','Motor PWM',('m1_pwm','m2_pwm','m3_pwm','m4_pwm'),('PWM 1','PWM 2','PWM 3','PWM 4'),'PWM Magnitude [uint16]','PWM Signal')
# # Battery Values
# include_log('pm','Power Management Battery',(['vbat']),(['Voltage Batt']),'Voltage [V]','Battery Voltage')
# # Pose Estimator
# include_log('posEstimatorAlt','Pose Estimator',('estimatedZ','velocityZ','estVZ'),('Esti Z','Vel Z','Esti Vel Z'),'Pose Estimator Data [?]','Pose Estimator')
# # Situation Awareness Flags
# include_log('sitAw','Situation Awareness',('ARDetected','TuDetected','FFAccWZDetected'),('At rest','tumbled','freefall'),'Enabled [bool]','Situation Awareness FLAGS')
# # Mellinger Controler Data
# include_log('ctrlMel','Controler Mellinger',('spR','spP','spY'),('spR','spP','spY'),'Setpoint Angular Rates [?]','Mellinger Setpoint Rates')
# include_log('ctrlMel','Controller Mellinger',('i_err_x','i_err_y','i_err_z'),('errorX','errorY','errorZ'),'?','Mellinger Position Error')
# Estimator Kalman Data
#include_log('estKal','Estimator Kalman',('pitch_e','roll_e'),('pitch estimated','roll estimated'),'pitch and roll [Deg]','Estimated Angles')
# Estimator KalmanUSC Data
plt.show()
