# https://libvirt.org/html/libvirt-libvirt-domain.html

# xml_data.xpath('/domain/metadata/nova:instance/nova:flavor', namespaces={'nova':'http://openstack.org/xmlns/libvirt/nova/1.0'})[0].values()

import libvirt
import os
import time
from xml.etree import ElementTree as etree

def read_cpu_time(instance_uuid):
    fp = open('/tmp/%s' % instance_uuid, 'r')
    t, cpuTime = fp.read().split()
    t = float(t)
    cpuTime = float(cpuTime)
    fp.close()
    return t, cpuTime

def write_cpu_time(instance_uuid, cpu_time):
    fp = open('/tmp/%s' % instance_uuid, 'w')
    fp.write('%s %s' % (time.time(), cpu_time))
    fp.close()

def calc_cpu_perc(instance_uuid, cpu_time):
    if not os.path.isfile('/tmp/%s' % instance_uuid):
        write_cpu_time(instance_uuid, cpu_time)
        return 0.0

    curT = time.time()
    curCpuTime = cpu_time
    prevT, prevCpuTime = read_cpu_time(instance_uuid)
    write_cpu_time(instance_uuid, cpu_time)

    return (curCpuTime - prevCpuTime) / ((curT - prevT) * 10000000)


conn = libvirt.openReadOnly("qemu:///system")
namespaces = {'nova':'http://openstack.org/xmlns/libvirt/nova/1.0'}

# dom_stats = conn.getAllDomainStats()

for instance in conn.listAllDomains():
    xml_data = etree.fromstring(instance.XMLDesc())
    uuid = xml_data.find('uuid').text
    name = xml_data.find('metadata/nova:instance/nova:name', namespaces=namespaces).text
    flavor = xml_data.find('metadata/nova:instance/nova:flavor', namespaces=namespaces).attrib['name']
    memory = xml_data.find('metadata/nova:instance/nova:flavor/nova:memory', namespaces=namespaces).text
    disk = xml_data.find('metadata/nova:instance/nova:flavor/nova:disk', namespaces=namespaces).text
    swap = xml_data.find('metadata/nova:instance/nova:flavor/nova:swap', namespaces=namespaces).text
    ephemeral = xml_data.find('metadata/nova:instance/nova:flavor/nova:ephemeral', namespaces=namespaces).text
    vcpus = xml_data.find('metadata/nova:instance/nova:flavor/nova:vcpus', namespaces=namespaces).text
    owner = xml_data.find('metadata/nova:instance/nova:owner/nova:user', namespaces=namespaces).text
    project = xml_data.find('metadata/nova:instance/nova:owner/nova:project', namespaces=namespaces).text

    state, reason = instance.state()  # https://libvirt.org/html/libvirt-libvirt-domain.html#virDomainState
    instance.getCPUStats(1)
    instance.memoryStats()
    instance.blockStats('vda') # VDA comes from XML -> devices/disk/target
    instance.interfaceStats('tapdd466195-98') # tap device from devices/interface/target
    instance.state() # Tells you if shut etc
