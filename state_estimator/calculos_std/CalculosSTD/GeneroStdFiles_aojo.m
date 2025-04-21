function []=GeneroStdFiles_aojo(jsonFileName,fch_stdjson)


stdExact=0.00001; % Std para medidas exactas (P=0, Q=0);
% Leer el archivo JSON
% [nudos,nudosname,imp]=CargoRedJson(NetFile);

fileID=fopen(jsonFileName,'r')
fileIDsave=fch_stdjson;

% Decodificar el archivo JSON
% jsonData = jsondecode(jsonText);

linea=fgetl(fileID);
lineasave=linea;

fileID2=fopen(fileIDsave,'w');
fprintf(fileID2, [lineasave '\n']);
while ~feof(fileID)
    linea=fgetl(fileID)
    dospuntos=find(linea==':');
    tipo=find(linea=='"');
    if isempty(tipo)==0
        tipo=tipo(1)+1;
        valor=abs(str2num(linea(dospuntos+1:end)));
        if length(find(linea=='_'))==1 %% medida de nudo, inyecciones
            if linea(tipo)=='U'
                std=0.0025; %las de ADGHRID MV salvo corrección por p o q pequeña
            elseif (linea(tipo)=='P')||(linea(tipo)=='Q')
                std=0.02;
                while floor(std/valor*10)>0; std=std/10;end % Correccion por valor pequeño en la medida
                if abs(valor)<=0.00001;std=stdExact;end % Si me paso de pequeña la dejo como las medidas exactas
            elseif linea(tipo)=='I'
                std=0.01;
                while floor(std/valor*10)>0; std=std/10;end % Correccion por valor pequeño en la medida
                if abs(valor)<=0.00001;std=stdExact;end % Si me paso de pequeña la dejo como las medidas exactas
            end
            lineasave=[linea(1:dospuntos) ' ' num2str(std,'%2.6f')];
            if strcmp(linea(end),',')==1
                lineasave=[lineasave linea(end)];%si tenía coma al final, la añado
            end
            fprintf(fileID2, [lineasave '\n']);
        elseif length(find(linea=='_'))>=2 %% medida de flujo
            if (linea(tipo)=='P')||(linea(tipo)=='Q')
                std=0.02;
                while floor(std/valor*10)>0; std=std/10;end % Correccion por valor pequeño en la medida
                if abs(valor)<=0.00001;std=stdExact;end % Si me paso de pequeña la dejo como las medidas exactas
            elseif linea(tipo)=='I'
                std=0.01;
                while floor(std/valor*10)>0; std=std/10;end % Correccion por valor pequeño en la medida
                if abs(valor)<=0.00001;std=stdExact;end % Si me paso de pequeña la dejo como las medidas exactas
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

