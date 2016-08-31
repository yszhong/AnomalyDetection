clear
rangem=[0.2,0.1];
parpool(length(rangem))
[~,siptext]=textread('../data/sip_score_z2_1.txt','%s%f'); %#ok<*DTXTRD>
[~,diptext]=textread('../data/dip_score_z6_1.txt','%s%f');
tpnum=1;
%[sip,dip]=textread('increment/edge_2015-06-19_12_num.txt','%d%d');
for zz=1:length(rangem)
    epsl=rangem(zz);
    sipscore=siptext;
    dipscore=diptext;
    m(:,:,1)=[1-2*epsl,2*epsl;epsl,1-epsl];
    %m(:,:,2)=[1-2*epsl,2*epsl;1-epsl,epsl];
    m(:,:,2)=m(:,:,1);
    matx{zz}=m;
end
clear m;
%[rsscore,dsscore]=myfnc(sipscore,dipscore,edge);
count=zeros(length(rangem));
mkdir('../result/z6_3/');
parfor zz=1:length(rangem)
    epsl=rangem(zz);
    result_sip=sipscore;
    result_dip=dipscore;
    
    %for i = 1:len

    %{
            filename = ['../data/increment1/',num2str(i),'.txt'];
            [sip,dip] = textread(filename,'%d%d');
            edge = [sip,dip];
    %}
    smat=matx{zz};
    dmat=smat(:,:,2);
    smat=smat(:,:,1);
    origin_dip=result_dip;
    origin_sip=result_sip;
    %[result_sip,result_dip]=mynewfnc(result_sip,result_dip,smat,dmat);
    [result_sip,result_dip]=refineagle(result_sip,result_dip,smat,dmat,epsl);
    %sipscore = result_sip;
    %dipscore = result_dip;
    for slen=1:length(result_sip)
        if abs(result_sip(slen)-0.5)>0.5
            result_sip(slen)=0.5+0.5*sign(result_sip(slen)-0.5);
        end
        if isnan(result_sip(slen))
            result_sip(slen)=origin_sip(slen);
        end
    end
    for dlen=1:length(result_dip)
        if isnan(result_dip(dlen))
            %disp(origin_dip);
            %error('Error: empty data!');
            result_dip(dlen)=origin_dip(dlen);
        end
        if(abs(result_dip(dlen)-0.5)>0.5)
            result_dip(dlen)=0.5+0.5*sign(result_dip(dlen)-0.5);
        end
    end
    %{
    if length(find(isnan(result_dip)))/length(result_dip)>0.6
        result_dip=origin_dip;
        result_sip=origin_sip;
        warning('Ignor the %dth time',len);
    end
    %}
    
    n=size(result_sip,1);
    fp=fopen(['../result/z6_3/sip_score' num2str(epsl) '.txt'],'wt');
    for i=1:n
        fprintf(fp,'%d\n',result_sip(i));
    end
    fclose(fp);
    
    n=size(result_dip,1);
    fp=fopen(['../result/z6_3/dip_score' num2str(epsl) '.txt'],'wt');
    for i=1:n
        fprintf(fp,'%d\n',result_dip(i));
    end
    fclose(fp);
    count(zz)=intersectverify(result_dip,tpnum);
    disp('verified');
end
delete(gcp)
bar(count);
hold on;
save('../result/z6_3/overlap.mat','count');
saveas(gcf,'../result/z6_3/overlap','fig');
saveas(gcf,'../result/z6_3/overlap','bmp');

disp('Succeed!');