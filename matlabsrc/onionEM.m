% realize the "onion" method
%
% Need matrixes in labeled10features.mat:
% badfeature: N*10, 10 features of bad IP
% goodfeature: N*10, 10 features of good IP
% 
% by Yunsong Zhong
clear;
load labeled10features.mat;
data=[badfeature;goodfeature];
label=[ones(length(badfeature),1);zeros(length(goodfeature),1)];
condition=1;
data=data(:,1:9);% the last column makes covariance not positive definite
while condition
    [W,M,V,L,P]=em(data,[],2,0,0,0);
    [~,Ind]=max(W);
    judge=length(P(P(:,Ind)>0.5))-length(badip);
    if judge<0
        condition=0;
    end
    Lst=P(:,Ind)>P(:,3-Ind);
    data=data(Lst,:);
    [~,sit]=sort(Lst);
    rlen=length(Lst(Lst~=0));
    tlen=length(Lst(Lst==0));
    ttru=length(find(label(sit(1:tlen))));
    rtru=length(find(label(sit(tlen+1:end))));
    label=label(Lst);
    disp([ttru,tlen,rtru,rlen])
    disp([ttru/tlen,rtru/rlen])
end
