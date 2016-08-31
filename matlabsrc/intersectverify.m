function count=intersectverify(dipscore,topnum)
% verify the intersection cluster
if nargin<2
    topnum=1;
end
[~,I]=sort(dipscore,'descend');
I=I+6788*ones(length(I),1);
%{
[table,~]=textread('../jupyter/iptable.txt','%s%d');
intersect=textread('../jupyter/dip-intersection.txt','%s');
suspect=textread('../jupyter/dip-suspect.txt','%s');
%% trans intersect
for i=1:length(intersect)
    for j=1:length(table)
        if strcmp(table{j},intersect{i})
            dint(i)=j;
        end
    end
end
for i=1:length(dipscore)
    for j=1:length(dint)
        if dint(j)==i
            ddet(j,1)=i;
        end
    end
end
%% find location of result

for i=1:length(I)
    for j=1:length(ddet)
        if I(i)==ddet(j,1)
            ddet(j,2)=i;
        end
    end
end
save(['../result/int_rank_z1/' num2str(nbst) '.mat'],'ddet');
%}
%% find overlap between methods

[rf,~]=textread('../data/black_list_compare.txt','%d%s');
%rf=rf(1:1000*topnum);
%{
disp('start reading');
rf=zeros(length(ip),1);
for i=1:length(ip)
    for j=1:length(table)
        if strcmp(table{j},ip{i})==1
            rf(i)=j;
        end
    end
end
%}
disp('calculating overlap');
%{
count=0;
%cnt=0;
for i=1:1000*topnum
    for j=1:length(rf)
        if I(i)==rf(j)
            count=count+1;
        end
    end
end
%}
count=length(intersect(rf(1:1000*topnum),I(1:1000*topnum)));
disp(count);
disp('done');
%count=count/(1000*topnum);
