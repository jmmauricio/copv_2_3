function []=GeneroStdFiles_SigmasProcedimiento(NetFile,jsonFileName,fch_stdjson,K)

IClass=0.5;VClass=0.5;PClass=0.5;QClass=1;


[nudos,nudosname,imp,Sbase]=CargoRedJson(NetFile);
% Sbase=100000000; %VA
% Vbase=[400 20000];%(V) LV, MV 
Vbase=sort(unique(nudos(:,end)),'descend'); %cargo todas las tensiones base
Ibase=(Sbase./Vbase)./sqrt(3);

%% valores de las tablas para U e I de errores para clase 0.5
minV_05=20; % minutos de error en la V de clase 0.5
ErrorEpsilonI=[1 5 20 100  120];
percentEpsilonI_05=[1.5 0.75 0.5 0.5 0.5];%fila de la tabla para clase 0.5S
minI_05=[90 45 30 30 30];%fila de la tabla para clase 0.5S

% PV plants with installed capacity close to 1 MWp have a CT with transformation ratio equal to 30/5A 
% PV with installed capacity less than 0.5 MWp have a CT with transformation ratio equal to 20/5A. 
% So, I suspect that the nominal current of the primary winding of the CT is equal to 30A and 20A, respectively.
relacion_transformI_LV_MV=[3000000/sqrt(3)/Vbase(end) 5]; %secundario siempre 5A, el otro lado es 3000/sqrt(3)/800, es decir,  
% %la corriente del PV a la maxima potencia, en el lado de LV
relacion_transformI_POI_MV=[3*3000000/sqrt(3)/Vbase(2)]; %porque hay 3 PV por linea
relacion_transformI_POI_MV_POI=[6*3000000/sqrt(3)/Vbase(1)]; %porque hay 3 PV por linea, y 2 lineas


% Leer el archivo JSON

fileID=fopen(jsonFileName,'r');
fileIDsave=fch_stdjson;

% Decodificar el archivo JSON
jsonText = fileread(jsonFileName);
jsonData = jsondecode(jsonText);
nombresCampos = fieldnames(jsonData);

linea=fgetl(fileID);
lineasave=linea;

fileID2=fopen(fileIDsave,'w');
fprintf(fileID2, [lineasave '\n']);
while ~feof(fileID)
    linea=fgetl(fileID);
    dospuntos=find(linea==':');
    tipo=find(linea=='"');
    if isempty(tipo)==0
        busmed=linea(tipo(1)+2:dospuntos-2);
        tipo=tipo(1)+1;
        valor=abs(str2num(linea(dospuntos+1:end)));
        if length(find(linea=='_'))==1 %medida de nudo, inyecciones
            if linea(tipo)=='U'
                epsilon_v=VClass;
                std=epsilon_v*valor/100/K;
            elseif (linea(tipo)=='P')||(linea(tipo)=='Q')
                % Encontrar el índice de los campos que contienen la parte conocida
                DatosU=['U' busmed];valorV=jsonData.(DatosU);
                DatosI=['I' busmed]; indiceCampos = contains(nombresCampos, DatosI);
                campoI=nombresCampos(find(indiceCampos==1));
                valorI=jsonData.(char(campoI));
                DatosP=['P' busmed];valorP=jsonData.(DatosP);
                DatosQ=['Q' busmed];valorQ=jsonData.(DatosQ);
                %std_vmag
                epsilon_v=VClass;
                std_vmag=epsilon_v*valorV/100/K; 
                %std_vang
                std_vang=minV_05/60*pi/180;
                %std_imag
                if strcmp(busmed(2:3),'LV')==1
                    relacion_transform_aqui=relacion_transformI_LV_MV(1);Ibase_aqui=Ibase(end);
                elseif strcmp(busmed(2:6),'POIMV')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV;Ibase_aqui=Ibase(2);
                elseif strcmp(busmed(2:5),'POI_')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV_POI;Ibase_aqui=Ibase(1);
                else
                    disp('error no encuentra nivel de Ibase')
                end
                rango_i=(valorI/(relacion_transform_aqui/Ibase_aqui))*100;%!!!!! p.u. y A
                epsilon_i=interpoloError(rango_i,ErrorEpsilonI,percentEpsilonI_05);
                std_imag=epsilon_i*valorI/100/K;
                % std_iang
                minI=interpoloError(rango_i,ErrorEpsilonI,minI_05);
                std_iang=minI/60*pi/180;

                if (linea(tipo)=='P')
                    std2=valorQ^2*(std_vang^2+std_iang^2)+valorP^2*((std_imag/valorI)^2+(std_vmag/valorV)^2);
                elseif (linea(tipo)=='Q')
                    std2=valorP^2*(std_vang^2+std_iang^2)+valorQ^2*((std_imag/valorI)^2+(std_vmag/valorV)^2);
                end
                std=sqrt(std2);
            elseif linea(tipo)=='I'
                if strcmp(busmed(2:3),'LV')==1
                    relacion_transform_aqui=relacion_transformI_LV_MV(1);Ibase_aqui=Ibase(end);
                elseif strcmp(busmed(2:6),'POIMV')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV;Ibase_aqui=Ibase(2);
                elseif strcmp(busmed(2:5),'POI_')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV_POI;Ibase_aqui=Ibase(1);
                else
                    disp('error no encuentra nivel de Ibase')
                end
                valorI=valor;
                rango_i=(valorI/(relacion_transform_aqui/Ibase_aqui))*100;%!!!!! p.u. y A
                epsilon_i=interpoloError(rango_i,ErrorEpsilonI,percentEpsilonI_05);
                std=epsilon_i*valor/100/K;
            end
            lineasave=[linea(1:dospuntos) ' ' num2str(std,'%2.6f')];
            if strcmp(linea(end),',')==1
                lineasave=[lineasave linea(end)];%si tenía coma al final la añado
            end
            fprintf(fileID2, [lineasave '\n']);

        elseif length(find(linea=='_'))>=2 %medida de flujo
            if (linea(tipo)=='P')||(linea(tipo)=='Q')
                % aux_=find(linea=='_');
                aux_=find(busmed=='_');
              % Encontrar el índice de los campos que contienen la parte conocida
                DatosU=['U' busmed(1:aux_(2)-1)];valorV=jsonData.(DatosU); %aqui correccion porque U solo de nudo, no de rama
                DatosI=['I' busmed]; indiceCampos = contains(nombresCampos, DatosI);
                campoI=nombresCampos(find(indiceCampos==1));
                valorI=jsonData.(char(campoI));
                DatosP=['P' busmed];valorP=jsonData.(DatosP);
                DatosQ=['Q' busmed];valorQ=jsonData.(DatosQ);
                %std_vmag
                epsilon_v=VClass;
                std_vmag=epsilon_v*valorV/100/K; 
                %std_vang
                std_vang=minV_05/60*pi/180;
                %std_imag
                if strcmp(busmed(2:3),'LV')==1
                    relacion_transform_aqui=relacion_transformI_LV_MV(1);Ibase_aqui=Ibase(end);
                elseif strcmp(busmed(2:6),'POIMV')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV;Ibase_aqui=Ibase(2);
                elseif strcmp(busmed(2:5),'POI_')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV_POI;Ibase_aqui=Ibase(1);
                else
                    disp('error no encuentra nivel de Ibase')
                end
                rango_i=(valorI/(relacion_transform_aqui/Ibase_aqui))*100;%!!!!! p.u. y A
                epsilon_i=interpoloError(rango_i,ErrorEpsilonI,percentEpsilonI_05);
                std_imag=epsilon_i*valorI/100/K;
                % std_iang
                minI=interpoloError(rango_i,ErrorEpsilonI,minI_05);
                std_iang=minI/60*pi/180;

                if (linea(tipo)=='P')
                    std2=valorQ^2*(std_vang^2+std_iang^2)+valorP^2*((std_imag/valorI)^2+(std_vmag/valorV)^2);
                elseif (linea(tipo)=='Q')
                    std2=valorP^2*(std_vang^2+std_iang^2)+valorQ^2*((std_imag/valorI)^2+(std_vmag/valorV)^2);
                end
                std=sqrt(std2);
            elseif linea(tipo)=='I'
                if strcmp(busmed(2:3),'LV')==1
                    relacion_transform_aqui=relacion_transformI_LV_MV(1);Ibase_aqui=Ibase(end);
                elseif strcmp(busmed(2:6),'POIMV')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV;Ibase_aqui=Ibase(2);
                elseif strcmp(busmed(2:5),'POI_')==1
                    relacion_transform_aqui=relacion_transformI_POI_MV_POI;Ibase_aqui=Ibase(1);
                else
                    disp('error no encuentra nivel de Ibase')
                end
                valorI=valor;
                rango_i=(valorI/(relacion_transform_aqui/Ibase_aqui))*100;%!!!!! p.u. y A
                epsilon_i=interpoloError(rango_i,ErrorEpsilonI,percentEpsilonI_05);
                std=epsilon_i*valor/100/K;
            end
            lineasave=[linea(1:dospuntos) ' ' num2str(std,'%2.6f')];
            if strcmp(linea(end),',')==1
                lineasave=[lineasave linea(end)];%si tenía coma al final la añado
            end
            fprintf(fileID2, [lineasave '\n']);
        end
    else %llave de cierre
        lineasave=linea;
        fprintf(fileID2, [lineasave '\n']);
    end
end
fclose(fileID)
fclose(fileID2)
fclose("all")

