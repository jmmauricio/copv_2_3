# Libraries
import numpy as np
import pandas as pd
import copy
import random
import json
import re

class grid:
    def __init__(self, nodes=None, lines=None, meas=None, constraints=None, path_topology=None, path_measurements=None):
        if path_topology and path_measurements:
            nodes, lines = system_topology(path_topology)
            constraints = system_constraints(nodes)
            meas = system_measurements(path_measurements, nodes, lines, add_noise = False)            
            self.nodes = self.add_nodes(nodes)                                      
            self.lines = self.add_lines(lines, self.nodes)   
            self.n = len(self.nodes)*2 - 1
            self.meas = self.add_meas(meas, self.nodes, self.lines, self.n)
            self.original_meas = meas
            self.H = np.zeros((len(self.meas), self.n))
            self.Y = self.build_Y()
            self.constraints = constraints
            self.constrained_meas = [measurement(item['id'], item['node'], item['line'], item['type'], item['value'], 0, self.nodes, self.lines, self.n) for index, item in enumerate(self.constraints)] 
        elif nodes and lines and meas and constraints:
            self.nodes = self.add_nodes(nodes)                                      
            self.lines = self.add_lines(lines, self.nodes)   
            self.n = len(self.nodes)*2 - 1
            self.meas = self.add_meas(meas, self.nodes, self.lines, self.n)
            self.original_meas = meas
            self.H = np.zeros((len(self.meas), self.n))
            self.Y = self.build_Y()
            self.constraints = constraints
            self.constrained_meas = [measurement(item['id'], item['node'], item['line'], item['type'], item['value'], 0, self.nodes, self.lines, self.n) for index, item in enumerate(self.constraints)] 
        else:
            raise ValueError("Either provide file paths or all required data (nodes, lines, meas, constraints).")
        
    def add_nodes(self, nodes):
        nodes_list = list()
        for item in nodes:
            nodes_list.append(node(item['id'], item['name'], item['B']))
        nodes_list[0].pointer = [None, len(nodes_list) - 1]
        for index, item in enumerate(nodes_list[1:]):
            item.pointer = [index, len(nodes_list) + index]
        return nodes_list
        
    def add_lines(self, lines, nodes):
        lines_list = list()
        for item in lines:
            lines_list.append(line(item['id'], item['From'], item['To'], item['R'], item['X'], item['B'], item['Transformer'], item['rt'], nodes))        
        return lines_list
    
    def add_meas(self, meas, nodes, lines, n):
        meas_list = list()
        for item in meas:
            meas_list.append(measurement(item['id'], item['node'], item['line'], item['type'], item['value'], item['std'], nodes, lines, n))
        return meas_list
    
    def state_estimation(self, tol = 1e-6, niter = 100, Huber = False, lmb = None, rn = False, print_info = True):
        flag, cond, value = True, True, None
        if print_info:
            print('')
            if Huber:
                print('Running Huber state estimator........')
            else:
                print('Running WLS state estimator........')
            print('')
        Results = {'solution': [], 'residual': [], 'jacobian': [], 'Q': [], 'std_sol': None, 'max_res': None, 'rm_meas': []}
        while (cond):
            x = np.array([0 for _ in range(int((self.n-1)/2))] + [1 for _ in range(int((self.n-1)/2)+1)])
            x_old = x*10
            self.build_W()
            self.assign(x)             
            self.compute_res(x)    
            self.Q = np.diag([1 for _ in self.res])
            self.build_H(x)            
            self.build_G(Huber = Huber)
            Results['solution'].append(x)
            Results['residual'].append(self.res)
            Results['jacobian'].append(self.H)
            Results['Q'].append(np.diag(self.Q))
            iteration = 1
            if print_info:
                print('')
            while (np.max(np.abs(x - x_old)) > tol) and (iteration < niter):
                x_old = x
                x = self.update_x(x, Huber = Huber)
                self.compute_res(x)   
                if iteration > 2:
                    self.build_Q(Huber = Huber, lmb = lmb)     
                self.build_H(x)
                self.build_G(Huber = Huber)
                Results['solution'].append(x)
                Results['residual'].append(self.res)
                Results['jacobian'].append(self.H)
                Results['Q'].append(np.diag(self.Q))
                if print_info:
                    print(f'Iteration {iteration}, residual: {np.linalg.norm(x - x_old):.8f}')     
                iteration += 1
            self.compute_mags()  
            if iteration >= niter:
                Results = {'solution': [], 'residual': [], 'jacobian': [], 'Q': [], 'std_sol': None, 'max_res': None, 'rm_meas': []}
                return Results
            # Std of the result
            if len(self.constrained_meas) == 0:
                self.std_sol = self.H.dot(np.linalg.inv(self.G).dot(self.H.T))
            else:
                A = np.block([[self.G, self.C],
                              [self.C.T, np.zeros((self.C.shape[1], self.C.shape[1]))]])
                U = np.linalg.inv(A)
                E1 = U[:self.G.shape[0], :self.G.shape[1]]
                if Huber:
                    self.std_sol = self.H @ E1 @ self.H.T @ self.Q @ self.W @ self.Q @ self.H @ E1.T @ self.H.T
                else:
                    self.std_sol = self.H @ E1 @ self.H.T @ self.W @ self.H @ E1.T @ self.H.T
                
            self.std_sol = np.sqrt(np.diag(self.std_sol))
            Results['std_sol'] = self.std_sol
            self.norm_res()
            if rn == False or Huber == True:
                cond = False
            else:
                max_index = np.argmax(self.res_norm)                
                if flag: # Me quedo con el primer resiudo máximo (normal) para luego parametrizar Lambda
                    max_res_value = np.max(np.abs(self.res))
                    max_res_index = list(np.abs(self.res)).index(max_res_value)                    
                    Results['max_res'] = np.abs(self.res[max_res_index]*np.sqrt(np.diag(self.W)[max_res_index]))
                    flag = False
                if self.res_norm[max_index] > 3:
                    if print_info:
                        print('')
                        print(f'Max. normalized resiudal: {self.res_norm[max_index]:.3f}')
                        print(f'Max. resiudal: {np.max(np.abs(self.res)):.3f}, {max_index}')
                    ref, tipo, value, std = self.meas[max_index].ref, self.meas[max_index].tipo, self.meas[max_index].value, self.meas[max_index].std
                    for index in range(len(self.original_meas)):
                        if self.original_meas[index]['id'] == ref and self.original_meas[index]['type'] == tipo and self.original_meas[index]['value'] == value and self.original_meas[index]['std'] == std:
                            Results['rm_meas'].append(index)
                            break                    
                    if print_info:
                        print(f'Deleting {self.meas[max_index].__dict__}')
                    self.meas.pop(max_index)
                else:
                    cond = False
        if print_info:
            print('')
        return Results
        
    def compute_mags(self):
        for node in self.nodes:
            node.Vx = complex(node.V*np.cos(node.theta), node.V*np.sin(node.theta))
        for line in self.lines:
            V1 = line.nodes[0].Vx
            V2 = line.nodes[1].Vx
            line.Ix = ((V1 - V2) / line.Z)
            line.I = np.abs(line.Ix)
            line.Pij = np.real(line.nodes[0].Vx*np.conj(line.Ix))
            line.Pji = -np.real(line.nodes[1].Vx*np.conj(line.Ix))
            line.Qij = np.imag(line.nodes[0].Vx*np.conj(line.Ix))
            line.Qji = -np.imag(line.nodes[1].Vx*np.conj(line.Ix))
        for node in self.nodes:
            node.Ix = np.sum([line.Ix if node == line.nodes[0] else -line.Ix for line in node.lines])
            node.I = np.abs(node.Ix)   
            node.P = np.real(node.Vx*np.conj(node.Ix))
            node.Q = np.imag(node.Vx*np.conj(node.Ix))     
        
    def build_H(self, x):
        self.assign(x)
        for index, m in enumerate(self.meas):
            m.compute_jacobian()            
        self.H = np.array([item.dh for item in self.meas])
        if len(self.constrained_meas) > 0:
            self.build_C(x)
        
    def build_C(self, x):
        for index, m in enumerate(self.constrained_meas):
            m.compute_jacobian()            
        self.C = np.array([item.dh for item in self.constrained_meas]).T
    
    def build_W(self):
        self.W = np.diag([1/(item.std**2) for item in self.meas])
        self.R = np.linalg.inv(self.W)
        
    def build_Q(self, lmb = 3, Huber = False):
        if Huber:
            self.Q = np.diag([(lmb/np.abs(item[0]))/np.sqrt(item[1]) if np.abs(item[0]*np.sqrt(item[1])) > lmb else 1 for item in zip(self.res, np.diag(self.W))])
        else:
            self.Q = np.eye(self.H.shape[0])
        
        
    def build_G(self, Huber = False):
        if Huber:
            self.G = self.H.T.dot(self.W).dot(self.Q).dot(self.H)
        else:
            self.G = self.H.T.dot(self.W).dot(self.H)
     
    def build_Y(self):
        self.Y = np.zeros((len(self.nodes), len(self.nodes)), dtype = complex)
        # Line: series elements
        for node in self.nodes:
            for line in node.lines:
                for line_con in line.nodes:
                    if node.ref != line_con.ref:
                        if line.Transformer == False:
                            self.Y[node.ref - 1, line_con.ref - 1] = -1/line.Z
        for index in range(self.Y.shape[0]):
            self.Y[index, index] = -np.sum(self.Y[index,:])
        # Line: parallel elements
        for node in self.nodes:
            for line in node.lines:
                for line_con in line.nodes:
                    if node.ref != line_con.ref:
                        if line.Transformer == False:
                            self.Y[node.ref - 1, node.ref - 1] += complex(0, line.Bpi)
        # Node: shunt elements
        for node in self.nodes:
            self.Y[node.ref - 1, node.ref - 1] += complex(0, node.Bshunt)
        # Power transformers
        for line in self.lines:
            if line.Transformer:
                index0 = line.nodes[0].ref - 1
                index1 = line.nodes[1].ref - 1
                Ycc, a = (1/line.Z), line.rt
                self.Y[index0, index0] += Ycc/(a**2)
                self.Y[index0, index1] += - Ycc/a
                self.Y[index1, index0] += - Ycc/a
                self.Y[index1, index1] += Ycc
            
        # Assigning G and B to the lines
        for node in self.nodes:
            for line in node.lines:
                for line_con in line.nodes:
                    if node.ref != line_con.ref:
                        line.G = np.real(self.Y[node.ref - 1, line_con.ref - 1])
                        line.B = np.imag(self.Y[node.ref - 1, line_con.ref - 1])
        # Assigning G and B to the nodes
        for node in self.nodes:
            node.G = np.real(self.Y[node.ref - 1, node.ref - 1])
            node.B = np.imag(self.Y[node.ref - 1, node.ref - 1])
        return self.Y        
        
    def assign(self, x):
        for index in range(len(self.nodes) - 1):
            self.nodes[1 + index].theta = x[index]        
        for index in range(len(self.nodes)):
            self.nodes[index].V = x[index + len(self.nodes) - 1]
            
    def compute_res(self, x):
        self.assign(x)
        self.res = [m.value - m.h() for m in self.meas]    
        self.c_res = [m.value - m.h() for m in self.constrained_meas] 
        
    def norm_res(self):
        M = self.R - self.std_sol
        self.res_norm = [item[0]/np.sqrt(item[1]) for item in zip(np.abs(self.res), np.diag(np.abs(M)))]
        
    def update_x(self, x, Huber = False):
        if len(self.constrained_meas) == 0:
            if Huber:
                return x + np.linalg.solve(self.G, self.H.T.dot(self.W).dot(self.Q).dot(self.res))
            else:
                return x + np.linalg.solve(self.G, self.H.T.dot(self.W).dot(self.res)) 
        else:
            A = np.block([[self.G, self.C],
                          [self.C.T, np.zeros((self.C.shape[1], self.C.shape[1]))]])
            if Huber:
                B = np.array(list(self.H.T.dot(self.W).dot(self.Q).dot(self.res)) + self.c_res)
                delta_x = np.linalg.solve(A, B)[:self.H.shape[1]]
                return x + delta_x
            else:
                B = np.array(list(self.H.T.dot(self.W).dot(self.res)) + self.c_res)
                delta_x = np.linalg.solve(A, B)[:self.H.shape[1]]
                return x + delta_x
                
    
    def report(self):
        for node in self.nodes:
            print(f'Node {node.name}: U = {node.V:.4f},\t  theta = {node.theta*180/np.pi:.3f}, \t Ix = {node.Ix:.3f}')
        print('')
        for line in self.lines:
            print(f'Line {str(line.nodes[0].name)+"-"+str(line.nodes[1].name)}: Ix = {line.Ix:.3f}')
        print('')
        print('\t\t\t\t\t\t meas. \t\t state \t\t res. ')
        for index, m in enumerate(self.meas):
            if m.tipo != 'i':
                print(f'{m.tipo}-{str(m.line.nodes[0].name)+"-"+str(m.line.nodes[1].name) if hasattr(m,"line") else str(m.node.name):15s}: \t {m.value:8.3f}  \t {m.h():8.3f}  \t {m.value-m.h():8.3f} ')
            else:
                print(f'{m.tipo}-{str(m.line.nodes[0].name)+"-"+str(m.line.nodes[1].name) if hasattr(m,"line") else str(m.node.name):15s}: \t {np.sqrt(m.value):8.3f}  \t {np.sqrt(m.h()):8.3f}  \t {m.value-m.h():8.3f}')
        print('')
                 
class node:
    def __init__(self, ref, name, B):
        self.ref = ref   
        self.name = name
        self.Bshunt = B
        self.lines = list()
        self.neigh = list()
        self.meas = list()
        self.V = 1
        self.theta = 0
        
    def check(self, currents = 0):
        Ilines = 0
        for line in self.lines:
            if line.nodes[0] == self:
                Ilines += line.I
            else:
                Ilines -= line.I
        Iloads = - complex(self.P, - self.Q)/np.conjugate(self.U) + currents
        return Ilines + Iloads 
    
class line:
    def __init__(self, ref, From, To, R, X, B, Transformer, rt, nodes_list):
        self.ref = ref 
        self.Transformer = Transformer
        self.rt = rt
        self.Bpi = B
        self.Z = complex(R, X)  
        self.G, self.B = -np.real(1/self.Z), -np.imag(1/self.Z)
        self.nodes = [next((item for item in nodes_list if item.name == From), None), 
                      next((item for item in nodes_list if item.name == To), None)]   
        self.nodes[0].lines.append(self)
        self.nodes[1].lines.append(self)
        self.nodes[0].neigh.append(self.nodes[1])
        self.nodes[1].neigh.append(self.nodes[0])
        self.meas = list()
        
    def check(self):
        res = self.Z*self.I - (self.nodes[0].U - self.nodes[1].U)
        res = self.I - self.Y*(self.nodes[0].U - self.nodes[1].U) 
        return res
  
class measurement:
    def __init__(self, ref, node_id, line_id, tipo, value, std, nodes, lines, n):
        self.ref = ref
        self.tipo = tipo
        self.value = value
        self.std = std
        self.n = n
        if node_id is not None:
            for n in nodes:
                if n.ref == node_id:
                    self.node = n
                    self.node_name = n.name
                    n.meas.append(self)
                    break
        if line_id is not None:
            if line_id < 0:
                self.sense = -1
                line_id = -line_id
            else:
                self.sense = 1
            for l in lines:
                if l.ref == line_id:
                    self.line = l
                    self.line_name = l.nodes[0].name + '-' + l.nodes[1].name 
                    l.meas.append(self)
                    break        
        if hasattr(self, 'node'):
            aux = [[self.node.pointer[0]], [self.node.pointer[1]], 
                  [n.pointer[0] for n in self.node.neigh], 
                  [n.pointer[1] for n in self.node.neigh]]
            self.pointer = [it for item in aux for it in item]
        if hasattr(self, 'line'):
            aux = [[self.line.nodes[0].pointer[0]], [self.line.nodes[0].pointer[1]], 
                  [self.line.nodes[1].pointer[0]], [self.line.nodes[1].pointer[1]]]
            self.pointer = [it for item in aux for it in item]
        
    def h(self):
        h = 'hola'
        if self.tipo == 'P' and hasattr(self, 'node'):
            h = self.Pi()
        if self.tipo == 'Q' and hasattr(self, 'node'):
            h = self.Qi()
        if self.tipo == 'P' and hasattr(self, 'line'):
            if self.sense > 0:
                h = self.Pij()
            else:
                h = self.Pji()
        if self.tipo == 'Q' and hasattr(self, 'line'):
            if self.sense > 0:
                h = self.Qij()
            else:
                h = self.Qji()
        if self.tipo == 'I' and hasattr(self, 'line'):
            if self.sense > 0:
                h = self.Iij()
            else:
                h = self.Iji()
        if self.tipo == 'U':
            h = self.V()   
        if h == 'hola':
            print('problemo')
        return h
        
    def compute_jacobian(self):         
        if self.tipo == 'U' and hasattr(self, 'node'):
            self.dh = np.zeros(self.n)
            self.dh[self.pointer[1]] = 1
        else:
            if hasattr(self, 'node'):
                if self.tipo == 'P':
                    aux = [it for item in [self.Pi_thetai(), self.Pi_Vi(), self.Pi_thetaj(), self.Pi_Vj()] for it in item]        
                if self.tipo == 'Q':
                    aux = [it for item in [self.Qi_thetai(), self.Qi_Vi(), self.Qi_thetaj(), self.Qi_Vj()] for it in item]    
            if hasattr(self, 'line'):
                if self.tipo == 'P':
                    aux = [it for item in [self.Pij_thetai(), self.Pij_Vi(), self.Pij_thetaj(), self.Pij_Vj()] for it in item]   
                if self.tipo == 'Q':
                    aux = [it for item in [self.Qij_thetai(), self.Qij_Vi(), self.Qij_thetaj(), self.Qij_Vj()] for it in item]  
                if self.tipo == 'I':
                    aux = [it for item in [self.Iij_thetai(), self.Iij_Vi(), self.Iij_thetaj(), self.Iij_Vj()] for it in item]  
                        
                        
            self.dh = np.zeros(self.n)
            for item in zip(self.pointer, aux):
                if item[0] != None:
                    self.dh[item[0]] = item[1]
                              
    # Partial derivatives        
    def Pij_Vi(self, line = None):
        Pij_Vi = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:
            dPij = node2.V*(line.G*np.cos(node1.theta - node2.theta) + line.B*np.sin(node1.theta - node2.theta)) - 2*line.G*node1.V
        else:
            dPij = node2.V*(line.G*np.cos(node2.theta - node1.theta) + line.B*np.sin(node2.theta - node1.theta)) 
        Pij_Vi.append(dPij)
        return Pij_Vi
     
    def Pij_Vj(self, line = None):
        Pij_Vj = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:
            dPij = node1.V*(line.G*np.cos(node1.theta - node2.theta) + line.B*np.sin(node1.theta - node2.theta))
        else:
            dPij = node1.V*(line.G*np.cos(node2.theta - node1.theta) + line.B*np.sin(node2.theta - node1.theta)) - 2*line.G*node2.V           
        Pij_Vj.append(dPij)
        return Pij_Vj
         
    def Qij_Vi(self, line = None):
        Qij_Vi = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:
            if line.Transformer:
                dQij = node2.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)) + 2*(line.B - line.Bpi[0])*node1.V
            else:
                dQij = node2.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)) + 2*(line.B - line.Bpi)*node1.V
        else:
           dQij = node2.V*(line.G*np.sin(node2.theta - node1.theta) - line.B*np.cos(node2.theta - node1.theta))  
        Qij_Vi.append(dQij)
        return Qij_Vi
     
    def Qij_Vj(self, line = None):
        Qij_Vj = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:
           dQij = node1.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)) 
        else:
            if line.Transformer:
                dQij = node1.V*(line.G*np.sin(node2.theta - node1.theta) - line.B*np.cos(node2.theta - node1.theta)) + 2*(line.B - line.Bpi[1])*node2.V
            else:
                dQij = node1.V*(line.G*np.sin(node2.theta - node1.theta) - line.B*np.cos(node2.theta - node1.theta)) + 2*(line.B - line.Bpi)*node2.V
        Qij_Vj.append(dQij)
        return Qij_Vj
         
    def Pij_thetai(self, line = None):
        Pij_thetai = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:  
            Pij_thetai.append(node1.V*node2.V*(-line.G*np.sin(node1.theta - node2.theta) + line.B*np.cos(node1.theta - node2.theta)))
        else:
            Pij_thetai.append(node1.V*node2.V*(line.G*np.sin(node2.theta - node1.theta) - line.B*np.cos(node2.theta - node1.theta)))
        return Pij_thetai
     
    def Pij_thetaj(self, line = None):
        Pij_thetaj = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:  
            Pij_thetaj.append(node1.V*node2.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)))
        else:
            Pij_thetaj.append(node1.V*node2.V*(-line.G*np.sin(node2.theta - node1.theta) + line.B*np.cos(node2.theta - node1.theta)))
        return Pij_thetaj
         
    def Qij_thetai(self, line = None):
        Qij_thetai = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:  
            Qij_thetai.append(node1.V*node2.V*(line.G*np.cos(node1.theta - node2.theta) + line.B*np.sin(node1.theta - node2.theta)))
        else:
            Qij_thetai.append(node1.V*node2.V*(-line.G*np.cos(node2.theta - node1.theta) - line.B*np.sin(node2.theta - node1.theta)))
        return Qij_thetai
     
    def Qij_thetaj(self, line = None):
        Qij_thetaj = list()
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if self.sense > 0:  
            Qij_thetaj.append(-node1.V*node2.V*(line.G*np.cos(node1.theta - node2.theta) + line.B*np.sin(node1.theta - node2.theta)))
        else:
            Qij_thetaj.append(-node1.V*node2.V*(-line.G*np.cos(node2.theta - node1.theta) - line.B*np.sin(node2.theta - node1.theta)))
        return Qij_thetaj
    
    def Iij_Vi(self, line = None):
        if line == None:
            line = self.line
        Vi = line.nodes[0].V
        Vj = line.nodes[1].V
        dPij = self.Pij_Vi(line)[0]
        dQij = self.Qij_Vi(line)[0]
        if self.sense > 0:
            Pij = self.Pij(line)
            Qij = self.Qij(line)
            return [(2/Vi**2)*(Pij*dPij + Qij*dQij) - (2/(Vi**3))*(Pij**2 + Qij**2)]
        else:
            Pji = self.Pji(line)
            Qji = self.Qji(line)
            return [(2/Vj**2)*(Pji*dPij + Qji*dQij)]
        
    def Iij_thetai(self, line = None):
        if line == None:
            line = self.line
        Vi = line.nodes[0].V
        Vj = line.nodes[1].V
        dPij = self.Pij_thetai(line)[0]
        dQij = self.Qij_thetai(line)[0]
        if self.sense > 0:
            Pij = self.Pij(line)
            Qij = self.Qij(line)
            return [(2/(Vi**2))*(Pij*dPij + Qij*dQij)]
        else:
            Pji = self.Pji(line)
            Qji = self.Qji(line)
            return [(2/(Vj**2))*(Pji*dPij + Qji*dQij)]
    
    def Iij_Vj(self, line = None):
        if line == None:
            line = self.line
        Vi = line.nodes[0].V
        Vj = line.nodes[1].V
        dPij = self.Pij_Vj(line)[0]
        dQij = self.Qij_Vj(line)[0]
        if self.sense > 0:
            Pij = self.Pij(line)
            Qij = self.Qij(line)
            return [(2/Vi**2)*(Pij*dPij + Qij*dQij)]
        else:
            Pji = self.Pji(line)
            Qji = self.Qji(line)
            return [(2/Vj**2)*(Pji*dPij + Qji*dQij) - (2/(Vj**3))*(Pji**2 + Qji**2)]
        
    def Iij_thetaj(self, line = None):        
        if line == None:
            line = self.line
        Vi = line.nodes[0].V
        Vj = line.nodes[1].V
        dPij = self.Pij_thetaj(line)[0]
        dQij = self.Qij_thetaj(line)[0]
        if self.sense > 0:
            Pij = self.Pij(line)
            Qij = self.Qij(line)
            return [(2/(Vi**2))*(Pij*dPij + Qij*dQij)]  
        else:
            Pji = self.Pji(line)
            Qji = self.Qji(line)
            return [(2/(Vj**2))*(Pji*dPij + Qji*dQij)]    
        
    def Pi_Vi(self):
        Pi_Vi = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Pi_Vi.append(neigh.V*(line.G*np.cos(self.node.theta - neigh.theta) + line.B*np.sin(self.node.theta - neigh.theta)))
        Pi_Vi.append(2*self.node.V*self.node.G)
        return [np.sum(Pi_Vi)]
     
    def Pi_Vj(self):
        Pi_Vj = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):                
            Pi_Vj.append(self.node.V*(line.G*np.cos(self.node.theta - neigh.theta) + line.B*np.sin(self.node.theta - neigh.theta)))
        return Pi_Vj
         
    def Qi_Vi(self):
        Qi_Vi = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Qi_Vi.append(neigh.V*(line.G*np.sin(self.node.theta - neigh.theta) - line.B*np.cos(self.node.theta - neigh.theta)))
        Qi_Vi.append(- 2*self.node.V*self.node.B)
        return [np.sum(Qi_Vi)]
     
    def Qi_Vj(self):
        Qi_Vj = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Qi_Vj.append(self.node.V*(line.G*np.sin(self.node.theta - neigh.theta) - line.B*np.cos(self.node.theta - neigh.theta)))
        return Qi_Vj
                  
    def Pi_thetai(self):
        Pi_thetai = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Pi_thetai.append(self.node.V*neigh.V*(-line.G*np.sin(self.node.theta - neigh.theta) + line.B*np.cos(self.node.theta - neigh.theta)) )
        return [np.sum(Pi_thetai)]
     
    def Pi_thetaj(self):
        Pi_thetaj = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Pi_thetaj.append(self.node.V*neigh.V*(line.G*np.sin(self.node.theta - neigh.theta) - line.B*np.cos(self.node.theta - neigh.theta)))
        return Pi_thetaj
         
    def Qi_thetai(self):
        Qi_thetai = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Qi_thetai.append(self.node.V*neigh.V*(line.G*np.cos(self.node.theta - neigh.theta) + line.B*np.sin(self.node.theta - neigh.theta)) )
        return [np.sum(Qi_thetai)]
     
    def Qi_thetaj(self):
        Qi_thetaj = list()
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Qi_thetaj.append(-self.node.V*neigh.V*(line.G*np.cos(self.node.theta - neigh.theta) + line.B*np.sin(self.node.theta - neigh.theta)))
        return Qi_thetaj
              
    # Magnitudes      
    def Pi(self):   
        Pi = 0
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Pi += self.node.V*neigh.V*(line.G*np.cos(self.node.theta - neigh.theta) + line.B*np.sin(self.node.theta - neigh.theta))
        return Pi + self.node.V*self.node.V*self.node.G
         
    def Qi(self):   
        Qi = 0
        for neigh, line in zip(self.node.neigh, self.node.lines):
            Qi += self.node.V*neigh.V*(line.G*np.sin(self.node.theta - neigh.theta) - line.B*np.cos(self.node.theta - neigh.theta))
        return Qi - self.node.V*self.node.V*self.node.B
         
    def Pij(self, line = None):         
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        Pij = node1.V*node2.V*(line.G*np.cos(node1.theta - node2.theta) + line.B*np.sin(node1.theta - node2.theta)) - line.G*(node1.V**2)
        return Pij
        
    def Pji(self, line = None):         
        if line == None:
            line = self.line
        node2 = line.nodes[0]
        node1 = line.nodes[1]
        Pij = node1.V*node2.V*(line.G*np.cos(node1.theta - node2.theta) + line.B*np.sin(node1.theta - node2.theta)) - line.G*(node1.V**2)
        return Pij
         
    def Qij(self, line = None):        
        if line == None:
            line = self.line
        node1 = line.nodes[0]
        node2 = line.nodes[1]
        if line.Transformer:
            Qij = node1.V*node2.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)) + (line.B - line.Bpi[0])*(node1.V**2)
        else:
            Qij = node1.V*node2.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)) + (line.B - line.Bpi)*(node1.V**2)
        return Qij  
         
    def Qji(self, line = None):        
        if line == None:
            line = self.line
        node2 = line.nodes[0]
        node1 = line.nodes[1]
        if line.Transformer:
            Qij = node1.V*node2.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)) + (line.B - line.Bpi[1])*(node1.V**2)
        else:
            Qij = node1.V*node2.V*(line.G*np.sin(node1.theta - node2.theta) - line.B*np.cos(node1.theta - node2.theta)) + (line.B - line.Bpi)*(node1.V**2)
        return Qij        
    
    def Iij(self, line = None):       
        if line == None:
            line = self.line
        Pij = self.Pij()
        Qij = self.Qij()
        return (Pij**2 + Qij**2) / line.nodes[0].V**2
    
    def Iji(self, line = None):       
        if line == None:
            line = self.line
        Pji = self.Pji()
        Qji = self.Qji()
        return (Pji**2 + Qji**2) / line.nodes[1].V**2
        
    def V(self):
        return self.node.V
        
        
# Building up functions        
def system_topology(file, U_base = 20e3):    
    with open(file, 'r') as f:
        data = json.load(f)        
    S_base_syst = data['system']['S_base']     
    Z_base = (U_base**2)/S_base_syst
    # Nodes list
    Nodes = list()
    index = 0
    for item in data['buses']:
        if item['name'] != 'BESS':
            Nodes.append({'name': item['name'], 
                          'id': index, 
                          'B': 0} )
            index += 1
    # Lines list
    Lines = list()
    index = 0
    for item in data['lines']:        
        if item['bus_j'] != 'BESS' and item['bus_k'] != 'BESS':
            if 'R_pu' in item.keys():
                Lines.append({
                    'id': index,
                    'From': item['bus_j'],
                    'To': item['bus_k'],
                    'R': item['R_pu']*S_base_syst/(item['S_mva']*1e6),
                    'X': item['X_pu']*S_base_syst/(item['S_mva']*1e6),
                    'B': item['Bs_pu']*(item['S_mva']*1e6/S_base_syst)/2, 
                    'Transformer': False,
                    'rt': 1
                    })
            else:
                Lines.append({
                    'id': index,
                    'From': item['bus_j'],
                    'To': item['bus_k'],
                    'R': item['R_km']*item['km']/Z_base,
                    'X': item['X_km']*item['km']/Z_base,
                    'B': item['Bs_km']*item['km']*Z_base/2, 
                    'Transformer': False,
                    'rt': 1
                    })            
            index += 1            
    # Transformers list
    index_lines = index 
    for index, item in enumerate(data['transformers']):
        Lines.append({
            'id': index_lines + index,
            'From': item['bus_j'],
            'To': item['bus_k'],
            'R': item['R_pu']*S_base_syst/(item['S_mva']*1e6),
            'X': item['X_pu']*S_base_syst/(item['S_mva']*1e6),
            'B': [0, 0], 
            'Transformer': True,
            'rt': 1
            })
    return Nodes, Lines
            
def system_constraints(Nodes):      
    nodenames = [node['name'] for node in Nodes]
    Cons = []
    index = 0
    for nn in nodenames:
        if "LV" in nn or "GRID" in nn:
            pass
        else:
            N = [d.get('id') if d.get('name') == nn else -1 for d in Nodes]
            N.sort()
            N = N[-1]
            Cons.append({
                'id': index,
                'node': N,
                'line': None,
                'type': 'P',
                'value': 0.0,
                })
            Cons.append({
                'id': index,
                'node': N,
                'line': None,
                'type': 'Q',
                'value': 0.0,
                })
            index += 2
    return Cons   

def system_measurements(file, Nodes, Lines, add_noise = False, corrientes = True):
    
    rt = {'LV':     3e6/(np.sqrt(3)*800),
          'POIMV':  3*3e6/(np.sqrt(3)*20e3),
          'POI':    6*3e6/(np.sqrt(3)*132e3)}
    I_base = {'LV':     3e6/(np.sqrt(3)*800),
              'POIMV':  3e6/(np.sqrt(3)*20e3),
              'POI':    3e6/(np.sqrt(3)*132e3)}
    Iclass = [[5, 20, 100, 120], [1.5, 0.75, 0.5, 0.5], [90, 45, 30, 30]]
    
    with open(file, 'r') as f:
        data = json.load(f)
    data_std = {key: None for key in data} 
    for key in data_std:
        if key.startswith('U'):
            data_std[key] = [0.0025*data[key], 20*np.pi/(60*180)]
        elif key.startswith('I'):
            value = (data[key]*I_base[re.sub(r'\d', '', key.split('_')[1])]/rt[re.sub(r'\d', '', key.split('_')[1])])*100
            epsilon_i_mag = np.interp(value, Iclass[0], Iclass[1])
            epsilon_i_ang = np.interp(value, Iclass[0], Iclass[2])
            data_std[key] = [epsilon_i_mag*data[key]/200, epsilon_i_ang*np.pi/(60*180)]
    for key in data_std:
        if key.startswith('P'):
            I_pointer = [key_aux for key_aux in data_std if key_aux.startswith('I_' + key.split('_')[1])][0]
            U_pointer = 'U_' + key.split('_')[1]
            Q_pointer = 'Q_' + key[2:]
            P_pointer = key
            data_std[key] = np.sqrt((data[Q_pointer]**2)*(data_std[U_pointer][1]**2 + data_std[I_pointer][1]**2) + (data[P_pointer]**2)*((data_std[I_pointer][0]/data[I_pointer])**2 + (data_std[U_pointer][0]/data[U_pointer])**2))   
        elif key.startswith('Q'):
            I_pointer = [key_aux for key_aux in data_std if key_aux.startswith('I_' + key.split('_')[1])][0]
            U_pointer = 'U_' + key.split('_')[1]
            P_pointer = 'P_' + key[2:]
            Q_pointer = key
            data_std[key] = np.sqrt((data[P_pointer]**2)*(data_std[U_pointer][1]**2 + data_std[I_pointer][1]**2) + (data[Q_pointer]**2)*((data_std[I_pointer][0]/data[I_pointer])**2 + (data_std[U_pointer][0]/data[U_pointer])**2))
    for key in data_std:
        if isinstance(data_std[key], list):
            data_std[key] = data_std[key][0]
            
    # List of measurements
    Meas = list()
    index_meas_id = 0
    for index_meas, item in enumerate(data.keys()):
        modified_item = item.split('_')
        # Measurement at node
        if len(modified_item) == 2:
            N = [d.get('id') if d.get('name') == modified_item[1] else -1 for d in Nodes]
            N.sort()
            N = N[-1]
            Meas.append({
                'id': index_meas_id,
                'node': N,
                'line': None,
                'type': modified_item[0],
                'value': data[item] if add_noise == False else data[item] + random.gauss(0, data_std[item]),
                'std': data_std[item]
                })     
            index_meas_id += 1
        # Measurement at line
        if len(modified_item) == 3:
            for l in Lines:
                if l['From'] == modified_item[1] and l['To'] == modified_item[2]:
                    id_l = l['id']
                    break
                if l['From'] == modified_item[2] and l['To'] == modified_item[1]:
                    id_l = -l['id']
                    break     
            value = data[item]**2 if modified_item[0] == 'I' else data[item]
            if add_noise and modified_item[0] != 'I':
                value += random.gauss(0, data_std[item])            
            if add_noise and modified_item[0] == 'I':
                value += random.gauss(0, 2*data_std[item]*data[item])
            if corrientes == True or (corrientes == False and modified_item[1].startswith('LV') == True):
                Meas.append({
                    'id': index_meas_id,
                    'node': None,
                    'line': id_l,
                    'type': modified_item[0],
                    'value': value,
                    'std': 2*data_std[item]*data[item] if modified_item[0] == 'I' else data_std[item],
                    })
                index_meas_id += 1  
    return Meas


def identification_fun(n_simus, names, net_base, bandas):
    # Data
    lmb_value = 2.5
    num_attacks = 1
        
    # Results
    count = {        
        'P': {'Precision': 0, 'Accuracy': 0, 'Recall': 0, 'F1': 0, 'norm2': 0, 'norminf': 0, 'z': 0},
        'Q': {'Precision': 0, 'Accuracy': 0, 'Recall': 0, 'F1': 0, 'norm2': 0, 'norminf': 0, 'z': 0},
        'U': {'Precision': 0, 'Accuracy': 0, 'Recall': 0, 'F1': 0, 'norm2': 0, 'norminf': 0, 'z': 0},
        'I': {'Precision': 0, 'Accuracy': 0, 'Recall': 0, 'F1': 0, 'norm2': 0, 'norminf': 0, 'z': 0}
    } 
    
    # Classification of the measurements to be attacked
    names_P = [names[index] for index in range(len(names)) if names[index].startswith('P_LV')]
    names_Q = [names[index] for index in range(len(names)) if names[index].startswith('Q_LV')]
    names_U = [names[index] for index in range(len(names)) if names[index].startswith('U_LV')] 
    names_I = [names[index] for index in range(len(names)) if names[index].startswith('I_LV')]    
    
    # For each type of attack (P, Q o U) we perform "n_simus" attacks              
    for names_ataque in [names_P, names_Q, names_U, names_I]:            
        for _ in range(n_simus):     
            net = copy.deepcopy(net_base)
            
            # Solving state estimation without attacks
            Results_clean = net.state_estimation(tol = 1e-4, niter = 50, Huber = True, lmb = lmb_value, rn = False)
            x_clean = Results_clean['solution'][-1][14:]
                        
            # Random choice of the measurement to be attacked             
            random_entries = random.sample(names_ataque, num_attacks)
            
            # We establish the amplitude of the attack based on "bandas"
            nums = []
            for ataque in random_entries:
                if ataque.startswith('P'):
                    num = names.index(ataque)
                    magnitud = bandas['P'][0] + np.random.rand()*bandas['P'][1]
                if ataque.startswith('Q'):
                    num = names.index(ataque)
                    magnitud = bandas['Q'][0] + np.random.rand()*bandas['Q'][1]
                if ataque.startswith('U'):
                    num = names.index(ataque)
                    magnitud = bandas['U'][0] + np.random.rand()*bandas['U'][1]                    
                if ataque.startswith('I'):
                    num = names.index(ataque)
                    magnitud = bandas['I'][0] + np.random.rand()*bandas['I'][1]
                z_exacta = net.meas[num].value
                net.meas[num].value = magnitud*net.meas[num].value                
                nums.append(num)
            
                
            # Running Huber state estimator
            Results_Huber = net.state_estimation(tol = 1e-4, niter = 50, Huber = True, lmb = lmb_value, rn = False)
            x_Huber = Results_Huber['solution'][-1][14:]
            z_estimada = net.meas[num].h()
            
            # Identification of the attack
            Q = np.array([list(Results_Huber['Q'][index]) for index in range(len(Results_Huber['Q']))]).T 
            n_cols = 3
            if Q.shape[1] < n_cols:
                result_rows = []  
            else:
                final_value_condition = Q[:, -1] < 1       
                
                def is_decreasing(row):
                    last_values = row[-n_cols:]
                    return np.all(np.diff(last_values) < 0)                
                
                filtered_rows = Q[final_value_condition]
                if len(filtered_rows) > 0:
                    decreasing_condition = np.array([is_decreasing(row) for row in filtered_rows])                                    
                    result_rows = np.where(final_value_condition)[0][decreasing_condition].tolist()       
                else:
                    result_rows = []  
                    
             # Clasificamos la identificación            
            TP, TN, FP, FN = 0, 0, 0, 0
            for i in range(len(net.meas)):
               is_attacked = i in nums # Attacked?               
               is_identified = i in result_rows # Well-identified?               
               
               # Classify the measurement and append to the appropriate list
               if is_attacked and is_identified:
                   TP += 1
               elif not is_attacked and not is_identified:
                   TN += 1
               elif not is_attacked and is_identified:
                   FP += 1
               elif is_attacked and not is_identified:
                   FN += 1
                   
            Precision = TP/(TP+FP) if TP + FP !=0 else 0
            Recall = TP/(TP+FN) if TP + FN !=0 else 0
            Accuracy = (TP+TN)/(TP+TN+FP+FN)
            F1 = 2*Precision*Recall/(Precision + Recall) if Precision + Recall !=0 else 0
            z = abs(z_estimada - z_exacta)
            
            
            if ataque.startswith('P'):
                count['P']['Precision'] += Precision
                count['P']['Recall'] += Recall
                count['P']['Accuracy'] += Accuracy
                count['P']['F1'] += F1
                count['P']['norm2'] += np.linalg.norm(x_clean - x_Huber, 2)/len(x_clean)
                count['P']['norminf'] += np.linalg.norm(x_clean - x_Huber, np.inf)
                count['P']['z'] += z
            if ataque.startswith('Q'):
                count['Q']['Precision'] += Precision
                count['Q']['Recall'] += Recall
                count['Q']['Accuracy'] += Accuracy
                count['Q']['F1'] += F1
                count['Q']['norm2'] += np.linalg.norm(x_clean - x_Huber, 2)/len(x_clean)
                count['Q']['norminf'] += np.linalg.norm(x_clean - x_Huber, np.inf)
                count['Q']['z'] += z
            if ataque.startswith('U'):
                count['U']['Precision'] += Precision
                count['U']['Recall'] += Recall
                count['U']['Accuracy'] += Accuracy
                count['U']['F1'] += F1
                count['U']['norm2'] += np.linalg.norm(x_clean - x_Huber, 2)/len(x_clean)
                count['U']['norminf'] += np.linalg.norm(x_clean - x_Huber, np.inf)  
                count['U']['z'] += z           
            if ataque.startswith('I'):
                count['I']['Precision'] += Precision
                count['I']['Recall'] += Recall
                count['I']['Accuracy'] += Accuracy
                count['I']['F1'] += F1
                count['I']['norm2'] += np.linalg.norm(x_clean - x_Huber, 2)/len(x_clean)
                count['I']['norminf'] += np.linalg.norm(x_clean - x_Huber, np.inf)
                count['I']['z'] += z
        
    for item in ['P', 'Q', 'U', 'I']:
        count[item]['Precision'] = count[item]['Precision']/(n_simus)
        count[item]['Recall'] = count[item]['Recall']/(n_simus)
        count[item]['Accuracy'] = count[item]['Accuracy']/(n_simus)  
        count[item]['F1'] = count[item]['F1']/(n_simus)  
        count[item]['norm2'] = count[item]['norm2']/(n_simus)  
        count[item]['norminf'] = count[item]['norminf']/(n_simus)  
        count[item]['z'] = count[item]['z']/(n_simus)    
             
    return count