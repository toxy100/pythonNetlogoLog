import string
import csv
import re
import datetime

filename = []
filename = open('./logfilelist.txt').read().split()
with open("reportlog.csv", 'wb') as f:
    writer = csv.writer(f)

    for filenum in range(len(filename)):
        with open("./nl_logs/" + filename[filenum], "r") as logfile:
            content = logfile.readlines()
            logfile.close()
            for i in range(len(content)):
                if 'username' in content[i]:
                    meta_info = content[i]
                if '<error' in content[i]:
                    interaction_starts = i
                if '</eventSet' in content[i]:
                    interaction_ends = i
                    break

            n = re.search(" name=\"(.)*\" i", meta_info)
            name_report = n.group(0)[7:-3]

            m = re.search(" modelName=\"(.)*\" v", meta_info)
            model_report = m.group(0)[12:-3]

            slider_events = []
            button_events = []
            custom_message = []

            for i in range(interaction_starts, interaction_ends):
                if "type=\"slider\"" in content[i]:
                    slider_name = content[i+2][10:-8]
                    slider_events.append([i, slider_name])
                if "type=\"button\"" in content[i] and "released" in content[i+2]:
                    button_name = content[i+1][10:-8]
                    button_events.append([i, button_name])
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
            if len(button_events) > 0:

                for i in range(len(button_events)):
                    temp = string.find(content[button_events[i][0]],"timestamp")
                    timestamp = content[button_events[i][0]][temp+11:temp+24]
                    button_events_report.append([timestamp,button_events[i][1]])

            custom_message_report = []
            if len(custom_message) > 0:

                for i in range(len(custom_message)):
                    temp = string.find(content[custom_message[i][0]],"timestamp")
                    timestamp = content[custom_message[i][0]][temp+11:temp+24]
                    custom_message_report.append([timestamp,custom_message[i][1]])

            list_length = len(slider_events_report) + len (button_events_report) + len (custom_message_report)
            combinedlist = []
            combinedlist = slider_events_report + button_events_report + custom_message_report
            combinedlist.sort()
            
            duration=[0]
            for i in range(len(combinedlist) - 1):
                duration.append(int(combinedlist[i+1][0][:-3]) - int(combinedlist[i][0][:-3]))
             

            for i in range(len(combinedlist)):
                combinedlist[i].insert(0,name_report)
                time = datetime.datetime.fromtimestamp(int(combinedlist[i][1][:-3])).strftime('%Y-%m-%d %H:%M:%S')
                combinedlist[i].insert(1,time)
                combinedlist[i].insert(1,model_report)
                combinedlist[i].insert(4,duration[i])
                
            print filename[filenum] + "processed"
            writer.writerows(combinedlist)
    
            

# there are cases in which button press and release don't appear in pairs.
# especially pay attention to go/pause which has different press and release time
