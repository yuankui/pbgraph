#!/bin/env python
import os
import sys
from google.protobuf import message
from google.protobuf.descriptor import FieldDescriptor as FD
import pydot as dot


class FieldGraph():
    def __init__(self,name,label):
        self.name = name
        self.label = label
    def get_name(self):
        return self.cls.get_name() + ':' + self.name

class ClassGraph():
    def __init__(self, name):
        self.field_list = []
        self.name = name

    def add_field(self, field):
        self.field_list.append(field)
        field.cls = self

    def get_name(self):
        return 'Class_' + self.name 

    def get_label(self):
        field_labels = map(lambda x: '<%s> %s' % (x.name, x.label), self.field_list)
        return ' | '.join(field_labels)

class EdgeManage():
    def __init__(self):
        self.set = set()

    def add_edge(self, src, to, label=''):
        self.set.add((src,to, label))

    def apply_edges(self, g):
        for src, to, label in self.set:
            e = dot.Edge(src, to)
            e.set('label', label)
            g.add_edge(e)

class PBGraph():

        
    def __str__(self):
        return self.g.to_string()

    def __init__(self):
        self.g = dot.Dot()
        self.g.set('rankdir', 'LR')
        self.edge_manage = EdgeManage()

    def get_graph(self):
        self.edge_manage.apply_edges(self.g)
        return self.g

    def add_subgraph(self, graph):
        self.g.add_subgraph(graph)

    def edge_exists(self, src, tar):
        t = (src.get_name(), tar.get_name())
        if t in self.edge_set:
            return True
        else:
            return False


    label_dict = {
            1: 'OPTIONAL',
            2: 'REQUIRED',
            3: 'REPEATED'
            }

    def draw(self, obj):
        global label_dict
        name = obj.name
    
        clsGraph = ClassGraph(name)
    
        title_Field = FieldGraph('class_' + name, 'CLASS:' + name)
        clsGraph.title_Field = title_Field
        clsGraph.add_field(title_Field)
        for field_name, field in obj.fields_by_name.items():
            fGraph = FieldGraph(field_name, field_name)
            clsGraph.add_field(fGraph)

            if field.message_type :
                fieldClass = self.draw(field.message_type)
                elabel = field.label
                self.edge_manage.add_edge(fGraph.get_name(), fieldClass.title_Field.get_name(), PBGraph.label_dict[elabel])
    
        node = dot.Node(clsGraph.get_name(), label = clsGraph.get_label())
        node.set('shape', 'record')
        self.g.add_node(node)
        return clsGraph



def usage():
    print 'app <in.proto> <output.png/jpg/svg>'

def main(argv):
    if len(argv) == 2:
        usage()
        sys.exit(1)
    sys.path.append('./tmp')
    proto_file = argv[1]
    out_file = argv[2]
    print out_file
    n = out_file.rfind('.')
    exec_name = out_file[n+1:]
    
    ## move the file to the temp
    tmp_file_name = 'aa'
    module_name = tmp_file_name + '_pb2'

    cmd = 'mkdir -p ./tmp'
    os.system(cmd)

    cmd = 'cp %s ./tmp/%s.proto' % (proto_file,tmp_file_name)
    os.system(cmd)

    cmd = 'cd tmp;protoc ./%s.proto --python_out=.' % (tmp_file_name)
    os.system(cmd)
    module = __import__(module_name)

    graph = PBGraph()
    for name,cls in module.DESCRIPTOR.message_types_by_name.items():
        graph.draw(cls)
    
    g = graph.get_graph()
    
    g.write(out_file ,format=exec_name)
    

if __name__ == '__main__':
    main(sys.argv)

