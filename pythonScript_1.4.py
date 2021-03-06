import string
import csv
import re
import datetime


#open the txt file that contains a list of log files to be processed
filename = []
filename = open('./logfilelist.txt').read().split()

#open an empty csv file to write values into it
with open("reportlog.csv", 'wb') as f:
    writer = csv.writer(f)

#open one logfile
    for filenum in range(len(filename)):
        with open("./nl_logs/" + filename[filenum], "r") as logfile:
            content = logfile.readlines()
            logfile.close()

#detect if this file is broken (interrupted by connection prblems, etc)
            brokenfile = False

            for i in range(len(content)):
                if 'terminated' in content[i]:
                    brokenfile = True
                
            if brokenfile == True:
                print filename[filenum] + " broken!"
                
#if it's an intact log file, locate username and interaction range
            else:
                for i in range(len(content)):
                    if '<code>' in content[i]:
                        done_loading = content[i-1]
                        break#find the first one then quit

                for i in range(len(content)):
                    if 'username' in content[i]:
                        meta_info = content[i]
                    if '<error' in content[i]:
                        interaction_starts = i
                    if '</eventSet' in content[i]:
                        interaction_ends = i
                        break

#search for student name and model name
                n = re.search(" name=\"(.)*\" i", meta_info)
                name_report = n.group(0)[7:-3]

                m = re.search(" modelName=\"(.)*\" v", meta_info)
                model_report = m.group(0)[12:-3]

                temp = string.find(done_loading,"timestamp")
                done_loading_time = done_loading[temp+11:temp+24]
                done_loading_report = [[done_loading_time, "Model Loaded"]]
                
#find slider, button, and custom message lines
                slider_events = []
                button_events = []
                custom_message = []

                for i in range(interaction_starts, interaction_ends):
                    if "type=\"slider\"" in content[i]:
                        slider_name = content[i+2][10:-8]
                        slider_events.append([i, slider_name])
                    if "type=\"button\"" in content[i]:
                        button_name = content[i+1][10:-8]
                        if "pressed" in content[i+2]:
                            button_events.append([i, button_name + " pressed"])
                        if "released" in content[i+2]:
                            button_events.append([i, button_name + " released"])
                    if "type=\"custom message\"" in content[i]:
                        message_content = content[i+1][13:-11]
                        custom_message.append([i,message_content])

                slider_events_report = []
                if len(slider_events) > 0:
                    slider_events_range = []
                    slider_event_start = int(slider_events[0][0])

                    for i in range(len(slider_events) - 1):
                        if slider_events[i][1] != slider_events[i+1][1]:
                            slider_events_range.append([slider_event_start, int(slider_events[i][0])])
                            slider_event_start = int(slider_events[i+1][0])
                    slider_events_range.append([slider_event_start, int(slider_events[len(slider_events)-1][0])])


                    for i in range(len(slider_events_range)):
                        temp = string.find(content[slider_events_range[i][1]],"timestamp")
                        timestamp = content[slider_events_range[i][1]][temp+11:temp+24]
                        slider_events_report.append([timestamp,content[slider_events_range[i][0] + 2][10:-8],content[slider_events_range[i][0] + 3][11:-9],content[slider_events_range[i][1] + 3][11:-9]])

                button_events_report = []
                button_events_delete = []
                if len(button_events) > 0:

                    for i in range(len(button_events)):
                        temp = string.find(content[button_events[i][0]],"timestamp")
                        timestamp = content[button_events[i][0]][temp+11:temp+24]
                        button_events_report.append([timestamp,button_events[i][1]])

                    for j in range(len(button_events_report)):
                        temp = button_events_report[j][1]
                        if temp[:8]!='go/pause' and temp[-8:]=='released':
                            button_events_report[j]='delete'
                        button_events_delete.append(button_events_report[j])

                    def remove_values_from_list(the_list, val):
                        while val in the_list:
                            the_list.remove(val)

                    remove_values_from_list(button_events_delete, 'delete')

                custom_message_report = []
                if len(custom_message) > 0:

                    for i in range(len(custom_message)):
                        temp = string.find(content[custom_message[i][0]],"timestamp")
                        timestamp = content[custom_message[i][0]][temp+11:temp+24]
                        custom_message_report.append([timestamp,custom_message[i][1]])

                list_length = len(done_loading_report) + len(slider_events_report) + len (button_events_report) + len (custom_message_report) 
                combinedlist = []
                combinedlist = done_loading_report + slider_events_report + button_events_report + custom_message_report
                combinedlist.sort()

                if len(combinedlist) > 0:
                    for i in range(len(combinedlist)):
                        temp = combinedlist[i][1]
                        if temp[:11]=='tick-count_':
                            combinedlist[i-1].extend(['','',temp[11:]])
                            combinedlist[i]='delete'

                remove_values_from_list(combinedlist, 'delete')
                
                duration=[0]
                for i in range(len(combinedlist) - 1):
                    duration.append(int(combinedlist[i+1][0][:-3]) - int(combinedlist[i][0][:-3]))
                 

                for i in range(len(combinedlist)):
                    combinedlist[i].insert(0,name_report)
                    time = datetime.datetime.fromtimestamp(int(combinedlist[i][1][:-3])).strftime('%Y-%m-%d %H:%M:%S')
                    combinedlist[i].insert(1,time)
                    combinedlist[i].insert(1,model_report)
                    combinedlist[i].insert(4,duration[i])
                    
                print filename[filenum] + " processed"
                writer.writerows(combinedlist)   
                
#V_1.5, Created by Bryan Guo for the ModelSim project. Dec. 16th 2013
