
function [nudos,nudosname,imp,Sbase]=CargoRedJson(jsonFileName)

% Leer el archivo JSON
% jsonFileName = 'archivo.json'; % Cambia 'archivo.json' por la ruta de tu archivo JSON
jsonText = fileread(jsonFileName);

% Decodificar el archivo JSON
jsonData = jsondecode(jsonText);

% Mostrar el contenido
disp(jsonData);

Sbase=jsonData.system.S_base;
%% nudos
NnudosOrig=size(jsonData.buses,1);
Nnudos=0;cont=0;

for k=1:NnudosOrig
    if (strcmp(jsonData.buses(k).name,'GRID')==0)&&(strcmp(jsonData.buses(k).name,'BESS')==0)
        cont=cont+1;
        Nnudos=Nnudos+1;
        nudosname{cont}=jsonData.buses(k).name;
        buses_redu(cont).name=jsonData.buses(k).name;
        U_V(cont,1)=jsonData.buses(k).U_kV*1000;
    end
end
nudos=[1:Nnudos]';nudos(:,2:8)=[zeros(Nnudos,4) ones(Nnudos,2) U_V];

%% lineas
NLinesOrig=size(jsonData.lines,1)
NLines=0;contL=0;
for k=1:NLinesOrig
    nomnudoi=jsonData.lines{k}.bus_j;
    nomnudoj=jsonData.lines{k}.bus_k;
if (strcmp(nomnudoi,'GRID')==0)&&(strcmp(nomnudoi,'BESS')==0)&&(strcmp(nomnudoj,'GRID')==0)&&(strcmp(nomnudoj,'BESS')==0)
    NLines=NLines+1;contL=contL+1;
    for kn=1:Nnudos
        if strcmp(buses_redu(kn).name,nomnudoi)==1
            nudoi(contL,1)=kn;
        end
        if strcmp(buses_redu(kn).name,nomnudoj)==1
            nudoj(contL,1)=kn;
        end
    end
    if isfield(jsonData.lines{k},'R_pu')==1
        Rpu(contL,1)=jsonData.lines{k}.R_pu;
        Xpu(contL,1)=jsonData.lines{k}.X_pu;
        Bspu(contL,1)=jsonData.lines{k}.Bs_pu;
    else
        Rpu(contL,1)=jsonData.lines{k}.R_km*jsonData.lines{k}.km;
        Xpu(contL,1)=jsonData.lines{k}.X_km*jsonData.lines{k}.km;
        Bspu(contL,1)=jsonData.lines{k}.Bs_km*jsonData.lines{k}.km;
    end
end
end

%% transformadores
Ntransformers=size(jsonData.transformers,1);
if Ntransformers==1
    nomnudoi=jsonData.transformers.bus_j;
    nomnudoj=jsonData.transformers.bus_k;
    for kn=1:Nnudos
        if strcmp(buses_redu(kn).name,nomnudoi)==1
            nudoi(1+NLines,1)=kn;
        end
        if strcmp(buses_redu(kn).name,nomnudoj)==1
            nudoj(1+NLines,1)=kn;
        end
    end
    if isfield(jsonData.transformers,'R_pu')==1
        Rpu(1+NLines,1)=jsonData.transformers.R_pu;
        Xpu(1+NLines,1)=jsonData.transformers.X_pu;
        Bspu(1+NLines,1)=jsonData.transformers.Bs_pu;
    else
        Rpu(1+NLines,1)=jsonData.transformers.R_km*jsonData.transformers.km;
        Xpu(1+NLines,1)=jsonData.transformers.X_km*jsonData.transformers.km;
        Bspu(1+NLines,1)=jsonData.transformers.Bs_km*jsonData.transformers.km;
    end
else
for k=1:Ntransformers
    nomnudoi=jsonData.transformers{k}.bus_j;
    nomnudoj=jsonData.transformers{k}.bus_k;    
    for kn=1:Nnudos
        if strcmp(buses_redu(kn).name,nomnudoi)==1
            nudoi(k+NLines,1)=kn;
        end
        if strcmp(buses_redu(kn).name,nomnudoj)==1
            nudoj(k+NLines,1)=kn;
        end
    end
    if isfield(jsonData.transformers{k},'R_pu')==1
    Rpu(k+NLines,1)=jsonData.transformers{k}.R_pu;
    Xpu(k+NLines,1)=jsonData.transformers{k}.X_pu;
    Bspu(k+NLines,1)=jsonData.transformers{k}.Bs_pu;
    else
    Rpu(k+NLines,1)=jsonData.transformers{k}.R_km*jsonData.transformers{k}.km;
    Xpu(k+NLines,1)=jsonData.transformers{k}.X_km*jsonData.transformers{k}.km;
    Bspu(k+NLines,1)=jsonData.transformers{k}.Bs_km*jsonData.transformers{k}.km;
    end
end
end

imp=[nudoi nudoj ones(NLines+Ntransformers,1) Rpu Xpu Bspu ones(NLines+Ntransformers,2) zeros(NLines+Ntransformers,2) ones(NLines+Ntransformers,1) zeros(NLines+Ntransformers,9)];





