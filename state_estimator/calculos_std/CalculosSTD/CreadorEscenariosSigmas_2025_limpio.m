

%% carga la red global que incluye trafos, y lee qué trafos se estiman de algún fichero con esa info
clear all
% clear;%randn('state',0);% resetea generador de ruido
path(path,genpath(cd)); % coloca carpetas de datos y programas en el path
% close all

MetodoSigma=2; %1: metodo AVJ-UF (preestablecido depende de Sn_equipo); 2: metodo bueno simplificado (depende de valor medido)

hora=["00";"01";"02";"03";"04";"05";"06";"07";"08";"09";"10";"11";"12";"13";"14";"15";"16";"17";"18";"19";"20";"21";"22";"23";"24"];
% hora=["08";"09";"10";"11";"12";"13";"14"];
min=["00";"15";"30";"45"];
fdp=["100";"090"]; %factor de potencia
negpos=["pos";"neg"]; 

%% _________LECTURA DE DATOS
for h=1:25 % bucle horas 
    for m=1:4 % bucle minutos
        for f=1:2 % bucle factor de potencia
            for n=1:f

                foldername=['pv_2_3_180_' num2str(hora(h)) '_' num2str(min(m)) '_pf_' num2str(fdp(f)) num2str(negpos(n))];

                fch_red='C:\Users\catal\OneDrive - UNIVERSIDAD DE SEVILLA\Proyectos\Activos\COCOON\Simulaciones\Datos\Red2x3_escenarios\pv_2_3.m'; %poner carpeta donde están los archivos de red
                fch_redjson=['C:\Users\Alvaro\OneDrive - UNIVERSIDAD DE SEVILLA\06 - Investigación\05 - Proyectos de Investigación\08 - COCOON\Estimador de estado\pv_2_3\copv_2_3\state_estimator\calculos_std\CalculosSTD\Red.json'];
                fch_medjson=['C:\Users\catal\OneDrive - UNIVERSIDAD DE SEVILLA\Proyectos\Activos\COCOON\Simulaciones\Datos\Escenarios\dataFeb2025\data\' foldername '\measurements.json']; %dirigir a donde estan los archivos de medidas
                fch_stdjson=[fch_medjson(:,1:end-5-12) 'std_' num2str(MetodoSigma) '.json']; %archivo en el que salvare std
                dt_exact=0.00001;Rest_igual=0;

                K=2;%factor cobertura
                if MetodoSigma == 1
                    GeneroStdFiles_aojo(fch_medjson,fch_stdjson)
                elseif MetodoSigma == 2
                    GeneroStdFiles_SigmasProcedimiento(fch_redjson,fch_medjson,fch_stdjson,K)
                end
            end
        end
    end
end

