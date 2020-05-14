% function beta=calcu(i,j)
E=10000;
Tn=2.65;
dlta_o=Tn/E;
beta=100;
dlta_f=10;
dlta_max=dlta_o*90;
ratio=dlta_max/dlta_f;


D=1-(dlta_o/dlta_max)*(1-(1-exp(-beta*((dlta_max-dlta_o)/(dlta_f-dlta_o))))/(1-exp(-beta)));

 dlta_o=0.8*dlta_o;

% dlta_f=dlta_f;
%·½³Ì
fun=@(beta)1-(dlta_o/dlta_max)*(1-(1-exp(-beta*((dlta_max-dlta_o)...
    /(dlta_f-dlta_o/2))))/(1-exp(-beta)))-D;
[beta,~]=fzero(fun,10);
% syms beta dlta_f dlta_max dlta_o D
% beta=solve([1-(dlta_o/2/dlta_max)*(1-(1-exp(-beta*((dlta_max-dlta_o/2)...
%     /(dlta_f-dlta_o/2))))/(1-exp(-beta)))-D==0],[beta])
% end
