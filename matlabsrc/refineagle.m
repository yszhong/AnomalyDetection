function [sipsc,dipsc ] = refineagle( sipscore,dipscore,edgesip,edgedip,epsl )
% speagle function


%% Natural logarithm
sipnum=size(sipscore,1);
sipnode=[log(1-sipscore),log(sipscore)];
dipnode=[log(1-dipscore),log(dipscore)];
%edgep=log(edgep);
edgesip=log(edgesip);
edgedip=log(edgedip);
[N, k1]=size(sipnode);
[M, k2]=size(dipnode);

sipbelief=zeros(N,k1);
dipbelief=zeros(M,k2);
fp=fopen('../result/z6_3/debug.txt','wt');
%% increment edge
for timeline=1:337
    %for timeline=1:2
    filename = ['../data/increment1/',num2str(timeline),'.txt'];
    [sip,dip] = textread(filename,'%d%d'); %#ok<*DTXTRD>
    edge = [sip,dip];
    
    disp(['epsilon=',num2str(epsl)]);
    %% Make 1s and 0s to 0.99 and 0.01 for iteration
    for a=1:M
        if(abs(dipscore(a)-0.5)>0.499)
            dipscore(a)=0.5+0.499*sign(dipscore(a)-0.5);
        end
    end
    
    E=size(edge,1);
    
    m_to=zeros(E,k1);
    m_from=zeros(E,k1);
    
    iter=0;
    delta=10^-6;
    iterstop=20;
    repeat=true;
    
    %% iterative message passing
    while(repeat)
        iter=iter+1;
        disp([num2str(iter),' iteration begins...']);
        maxdiff=-Inf;
        %% message to destination
        nM=zeros(M+N,2);
        sumN=zeros(N,k1);
        for i=1:E
            sumN(edge(i,1),:)= sumN(edge(i,1),:)+m_from(i,:);
            nM(edge(i,1),:)=nM(edge(i,1),:)+1;
        end
        
        alldiff=zeros(2*E,1);
        
        %compute message to N dip nodes
        
        for i=1:E
            a=edge(i,1);
            mn=sumN(a,:)-m_from(i,:);
            if nM(a)
                mn=mn/nM(a);
            end
            part=sipnode(a,:)+mn;
            %part=dipnode(edge(i,2)-sipnum,:)+mn;
            newmsg=zeros(1:k1);
            for k=1:k1
                %term = ( part + edgep( k,: ) );
                term = ( part + edgesip( k,: ) );
                newmsg(k) = log(sum(exp(term-max(term)))) + max(term);
            end
            newmsg = newmsg-( log(sum(exp(newmsg-max(newmsg)))) + max(newmsg) );
            fark = exp(newmsg) - exp(m_to(i,:));
            diff = norm(fark);
            alldiff(i) = diff;
            m_to(i,:)=newmsg;
            if(diff > maxdiff)
                maxdiff = diff;
            end
            %{
            if edge(i,2)==203030
                fprintf(fp,'to: %s, source: %s, total:%s\n',num2str(m_to(i,:)),num2str(edge(i,1)),num2str(sum(exp(m_to(i,:)))));
            end
            %}
        end
        %ending sipnode
        
        %% message from destination
        sumM=zeros(M,k2);
        begin=sipnum;
        for i=1:E
            sumM(edge(i,2)-begin,:)= sumM(edge(i,2)-begin,:)+m_to(i,:);
            nM(edge(i,2))=nM(edge(i,2))+1;
        end
        
        for i=1:E
            
            a=edge(i,2);
            mn=sumM(a-begin,:)-m_to(i,:);
            %{
            if edge(i,2)==203030
                fprintf(fp,'mn=%s\t',num2str(mn));
            end
            %}
            if nM(a)
                mn=mn/nM(a);
            end
            part=dipnode(a-begin,:)+mn;
            %part=sipnode(edge(i,1),:)+mn;
            newmsg=zeros(1,k2);
            for k=1:k2
                %term = ( part + edgep( :,k )' );
                term = ( part + edgedip( k,: ) );
                newmsg(k) = log(sum(exp(term-max(term)))) + max(term);
            end
            %{
            if edge(i,2)==203030
                fprintf(fp,'newmsg:%s\t',num2str(newmsg));
            end
            %}
            newmsg = newmsg-( log(sum(exp(newmsg-max(newmsg)))) + max(newmsg) );
            
            fark = exp(newmsg) - exp(m_from(i,:));
            diff = norm(fark);
            alldiff(i+E) = diff;
            if( diff > maxdiff)
                maxdiff = diff;
            end
            m_from(i,:) = newmsg;
            %{
            if edge(i,2)==203030
                fprintf(fp,'from: %s, source: %s, total:%s\n',num2str(m_from(i,:)),num2str(edge(i,1)),num2str(sum(exp(m_from(i,:)))));
            end
            %}
        end
        %{
    maxd = max(alldiff);
    mind = min(alldiff);
    meand = mean(alldiff);
    p90 = quantile(alldiff, 0.9);
        %}
        %% stop condition
        if maxdiff < delta
            repeat = false;
        end
        if(iter>iterstop)
            break;
        end
        
    end
    disp([num2str(iter),' times looping end']);
    disp(['Time ',num2str(timeline),' loaded...'])
end
%% compute belief
begin=sipnum;

for i=1:E
    a=edge(i,1);
    b=edge(i,2)-begin;
    sipbelief(a,:)=sipbelief(a,:)+m_from(i,:);
    dipbelief(b,:)=dipbelief(b,:)+m_to(i,:);
    %{
        if edge(i,2)==203030
            fprintf(fp,'belief: %s, m_to:%s, from:%s, sr:%s\n',num2str(dipbelief(b,:)),num2str(m_to(i,:)),num2str(m_from(i,:)),num2str(edge(i,1)));
        end
        if edge(i,2)==149887
            fprintf(fp,'g-belief: %s, m_to:%s, from:%s, sr:%s\n',num2str(dipbelief(b,:)),num2str(m_to(i,:)),num2str(m_from(i,:)),num2str(edge(i,1)));
        end
    %}
end


for a=1:N
    sipbelief(a,:)=sipnode(a,:)+sipbelief(a,:);
    nwm=sipbelief(a,:);
    for k=1:k1
        sipbelief(a,k)=-log(sum(exp(nwm-nwm(k))));
    end
    if(abs(sipbelief(a,1))<0.01||abs(sipbelief(a,2)-1)<0.01)
        sipbelief(a,:)=[0.01,0.99];
    end
    if(abs(sipbelief(a,2))<0.01||abs(sipbelief(a,1)-1)<0.01)
        sipbelief(a,:)=[0.99,0.01];
    end
end

for a=1:M
    dipbelief(a,:)=dipnode(a,:)+dipbelief(a,:);
    nwm=dipbelief(a,:);
    for k=1:k1
        dipbelief(a,k)=-log(sum(exp(nwm-nwm(k))));
    end
    
    if(abs(exp(dipbelief(a,1)))<0.0001||abs(exp(dipbelief(a,2)-1))<0.0001)
        dipbelief(a,:)=[log(0.0001),log(0.9999)];
    end
    if(abs(exp(dipbelief(a,2)))<0.0001||abs(exp(dipbelief(a,1)-1))<0.0001)
        dipbelief(a,:)=[log(0.9999),log(0.0001)];
    end
    
    
    if a+sipnum==203030
        fprintf(fp,'belief:%s, sum:%s\n',num2str(dipbelief(a,:)),num2str(sum(exp(dipbelief(a,:)))));
    end
    if a+sipnum==149887
        fprintf(fp,'belief:%s, sum:%s\n',num2str(dipbelief(a,:)),num2str(sum(exp(dipbelief(a,:)))));
    end
    if a+sipnum==215138
        fprintf(fp,'belief:%s, sum:%s\n',num2str(dipbelief(a,:)),num2str(sum(exp(dipbelief(a,:)))));
    end
    if a+sipnum==267156
        fprintf(fp,'belief:%s, sum:%s\n',num2str(dipbelief(a,:)),num2str(sum(exp(dipbelief(a,:)))));
    end
end
disp('belief generated');

%% use second column as bad score
sipsc = exp(sipbelief(:,2));
dipsc = exp(dipbelief(:,2));

%% judge normal dipscore
for i=1:M
    if isnan(dipsc(i))
        dipsc(i)=dipscore(i);
    end
end

fclose(fp);
disp('loop ending')
end
