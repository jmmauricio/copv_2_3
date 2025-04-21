function[y]=interpoloError(x,Xvect,Yvect)
aux=find(Xvect<=x);

if isempty(aux)==1 %si no ha encontrado ninguno valor menor, cojo el primero
    y=Yvect(1);
elseif length(aux)==length(Xvect)%todos son menores
    y=Yvect(end);
else

    x_points = [Xvect(aux(end)), Xvect(aux(end)+1)];
    y_points = [Yvect(aux(end)), Yvect(aux(end)+1)];

    % Realiza la interpolación lineal
    y = interp1(x_points, y_points, x, 'linear');
end
