rng(100)

med3x2PV_ok

%% meto ruido
mmedten(:,2)=mmedten(:,2)+randn(size(mmedten,1),1).*mmedten(:,3);
auxP0=find(mmedinyp(:,2)<=0.00001);
auxQ0=find(mmedinyq(:,2)<=0.00001);
mmedinyp(:,2)=mmedinyp(:,2)+randn(size(mmedinyp,1),1).*mmedinyp(:,3);mmedinyp(auxP0,2)=0;
mmedinyq(:,2)=mmedinyq(:,2)+randn(size(mmedinyq,1),1).*mmedinyq(:,3);mmedinyq(auxQ0,2)=0;
mmedflujop(:,4)=mmedflujop(:,4)+randn(size(mmedflujop,1),1).*mmedflujop(:,5);
mmedflujq(:,4)=mmedflujq(:,4)+randn(size(mmedflujq,1),1).*mmedflujq(:,5);
if  isempty(mmedflujI2)==0
mmedflujI2(:,4)=mmedflujI2(:,4)+randn(size(mmedflujI2,1),1).*mmedflujI2(:,5);
end