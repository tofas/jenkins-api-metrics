import jenkins
import urllib2
import collections
import re
import Constants

def get_server_instance():
    server = jenkins.Jenkins(Constants.JENKINS_URL, Constants.USERNAME, Constants.PASSWORD)
    return server

def get_counters(server):
    info = server.get_job_info(Constants.CURRENT_JOB, fetch_all_builds = True)
    builds = info['builds']
    no_device_counter = 0
    fail_counter = 0
    success_counter = 0
    failing_tests_total = 0
    total_builds = 0
    espresso_fail_counter = 0
    fail_tests_min_1 = 0
    fail_tests_min_2 = 0
    fail_tests_more_2 = 0
    for build in builds:
        try:
            info = server.get_build_info(Constants.CURRENT_JOB, build['number'])
            output = server.get_build_console_output(Constants.CURRENT_JOB, build['number'])
            if info['result'] == Constants.FAILURE:
                fail_counter += 1
                total_builds += 1
                words = re.findall(Constants.NO_CONNECTED_DEVICES, output)
                results = collections.Counter(words)
                if results[Constants.NO_CONNECTED_DEVICES] == 0:
                    words = re.findall(Constants.DEVICE_OFFLINE, output)
                    results = collections.Counter(words)
                    if results[Constants.DEVICE_OFFLINE] == 0:
                        words = re.findall(Constants.FAILED_SCENARIO, output)
                        results = collections.Counter(words)
                        word_counter = results[Constants.FAILED_SCENARIO]
                        failing_tests_total += word_counter
                        if word_counter == 1:
                            fail_tests_min_1 += 1
                        if word_counter == 2:
                            fail_tests_min_2 += 1
                        if word_counter > 2:
                            fail_tests_more_2 += 1
                        if word_counter > 0:
                            espresso_fail_counter += 1
                    else:
                        no_device_counter += 1
                else:
                    no_device_counter += 1
                # Uncomment line below to see the output per build
                # print str(build['number']) + " " + str(results)
            elif info['result'] == Constants.SUCCESS:
                success_counter += 1
                total_builds += 1
        except Exception as e:
            print 'Could not parse ' + str(build['number'])
            print e
    
    return no_device_counter, fail_counter, success_counter, failing_tests_total, total_builds, espresso_fail_counter, fail_tests_min_1, fail_tests_min_2, fail_tests_more_2

def print_results(no_device_counter, fail_counter, success_counter, failing_tests_total, total_builds, espresso_fail_counter, fail_tests_min_1, fail_tests_min_2, fail_tests_more_2):
    print 'Success: ' + str(success_counter)
    print 'Failure: ' + str(fail_counter)
    print 'Total tests failing: ' + str(failing_tests_total)
    print 'No device connected errors: ' + str(no_device_counter)
    print 'Espresso failing builds: ' + str(espresso_fail_counter)
    print 'Espresso test failing with 1 fail ' + str((fail_tests_min_1/float(espresso_fail_counter))*100)
    print 'Espresso test failing with 2 fail ' + str((fail_tests_min_2/float(espresso_fail_counter))*100)
    print 'Espresso test failing more than 2 fails ' + str((fail_tests_more_2/float(espresso_fail_counter))*100)
    print 'Average # of tests failing per failed build: ' + str(fail_counter/float(espresso_fail_counter))
    print 'Success rate: ' + str((success_counter/float(total_builds))*100)
    print 'Fail rate: ' + str((fail_counter/float(total_builds))*100)
    print 'No connected devices over total rate: ' + str((no_device_counter/float(total_builds))*100)
    print 'No connected devices over failures rate: ' + str((no_device_counter/float(fail_counter))*100)
    print 'Total builds ' + str(total_builds)

if __name__ == '__main__':
    server = get_server_instance()
    no_device_counter, fail_counter, success_counter, failing_tests_total, total_builds, espresso_fail_counter, fail_tests_min_1, fail_tests_min_2, fail_tests_more_2 = get_counters(server)
    print_results(no_device_counter, fail_counter, success_counter, failing_tests_total, total_builds, espresso_fail_counter, fail_tests_min_1, fail_tests_min_2, fail_tests_more_2)
   