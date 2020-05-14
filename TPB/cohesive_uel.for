c
c    ͨ�����Է��ָ�˹���ֲ���ţ��-cotes���ֺ�ʹ��ʹ�ø�˹����ʱ���׳���
c    ͨ�����Է��ּ�������abaqus�����һ��
c     LINEAR EXPONENT BILINEAR PPR
c                     2019��6��30��
c
      SUBROUTINE UEL(RHS,AMATRX,SVARS,ENERGY,NDOFEL,NRHS,NSVARS,
     1 PROPS,NPROPS,COORDS,MCRD,NNODE,U,DU,V,A,JTYPE,TIME,DTIME,
     2 KSTEP,KINC,JELEM,PARAMS,NDLOAD,JDLTYP,ADLMAG,PREDEF,NPREDF,
     3 LFLAGS,MLVARX,DDLMAG,MDLOAD,PNEWDT,JPROPS,NJPROP,PERIOD)
c
C
      INCLUDE 'ABA_PARAM.INC'
C
      parameter(zero=0.d0,half=0.5d0,one=1.d0,two=2.d0,three=3.d0,
     1 four=4.d0,five=5.d0,NELEMENT=25306.d0,NINPT=2.d0,NSVINT=7.d0,
     2 ELEMOFFSET=83200.d0)
c
      DIMENSION RHS(MLVARX,*),AMATRX(NDOFEL,NDOFEL),PROPS(*),
     1 SVARS(NSVARS),ENERGY(8),COORDS(MCRD,NNODE),U(NDOFEL),
     2 DU(MLVARX,*),V(NDOFEL),A(NDOFEL),TIME(2),PARAMS(*),
     3 JDLTYP(MDLOAD,*),ADLMAG(MDLOAD,*),DDLMAG(MDLOAD,*),
     4 PREDEF(2,NPREDF,NNODE),LFLAGS(*),JPROPS(*)
c    
      dimension stress(2),ddsdde(2,2),gauss(2),weight2(2),
     1 cotnew(2),cweight(2),dndxi(2),dlta_u(4),du_cont(MCRD),
     2 du_loc(MCRD),H(mcrd,4),c_coor(mcrd,nnode),psi(4,ndofel),
     3 B(mcrd,ndofel),BT(ndofel,mcrd),A1(ndofel,mcrd),
     4 A2(ndofel,ndofel),AV_coor(mcrd,2),V_XI(mcrd),V_N(mcrd),
     5 THETA(2,2),THETAT(2,2),str_glob(2),D_GLOB(mcrd,mcrd),
     6 DD1(mcrd,mcrd),vu_cont(MCRD),VU_loc(MCRD)
      
      REAL*8 UVAR,alpha,dlta_zero
      COMMON/KUSER/UVAR(NELEMENT,NSVINT,NINPT)
      
	data iuel/0/
	save iuel
      
c      if(KINC.gt.0)then
c      read *
c      end if  
c      write(7,*)'��Ԫ=',JELEM

c
c
c     ��Ԫ�ڵ��� 4
c     ndofel=8
c     mcrd=2    (x,y)
c     �����ʼ��
      call kaset2(rhs,mlvarx,1)
	call kaset2(amatrx,ndofel,ndofel)
	call kaset2(psi,4,ndofel)
	call kaset2(H,2,4)
      
      
c
      width=props(8)
c
c    �����������
      nintp=jprops(1)   !���ֵ����
      ints=jprops(2)    !���ֵ�ѡȡ��1����˹���֣�2��newton-cotes���֣�
      

c    
c      �����Ϣ�����
c      if (iuel.eq.0)then
c       open(15,file='c:/xiaohe/verify.out')
c	  write(7,*)'-----��һ�ε�ȡuel-------------------'
c	  write(7,*)'�ܵ����ɶ���',ndofel
c	  write(7,*)'�ڵ���',nnode
c	  write(7,*)'���ֵ���',nintp
c	  write(7,*)'���ַ���',ints
c	  write(7,*)'���������',mcrd
c	  write(7,*)'״̬������',nsvars
c	iuel=1
c	end if
c      
      do i=1,ndofel/2
	  psi(i,i)=-one
C      psi(i,i+ndofel/2)=one
      end do
      psi(1,7)=one
      psi(2,8)=one
      psi(3,5)=one
      psi(4,6)=one

c
c      ������κ�����
       do i=1,mcrd
	  do j=1,nnode
	   nn=i+(j-1)*mcrd
	   c_coor(i,j)=coords(i,j)+u(nn)
	  end do
       end do
c      write(7,*)'�ڵ�λ��', u
c	write(7,*)'����',coords(1,1),coords(1,2),coords(1,3),coords(1,4)

c
c
c      �����м�ƽ������
      
       do i=1,mcrd
	  do j=1,nnode/2
	   AV_coor(i,j)=one/two*(c_coor(i,j)+c_coor(i,5-j))
c         AV_coor(i,j)=one/two*(c_coor(i,j)+c_coor(i,j+nnode/2))
        end do
       end do
c      write(7,*)'A������',AV_coor(1,1),AV_coor(1,2)
c      
c      ���û��ֵ�ͼ�Ȩϵ��
c       
c      ��˹����
      Gauss(1)=-one/sqrt(three)
	Gauss(2)=-Gauss(1)
	weight2(1)=one
	weight2(2)=one
c      newton-cotes����
      cotnew(1)=-one
	cotnew(2)=one
	cweight(1)=one
      cweight(2)=one
c
c     ��ʼ���ֵ�ѭ��
c 
      do 100 iintp=1,nintp
c
	if(ints.eq.1)then 
	   point=Gauss(iintp)
	   weight=weight2(iintp)
	 else
	   point=cotnew(iintp)
	   weight=cweight(iintp)
	end if
c	      
c     ����ڵ����κ���ֵ
c
      H1=half*(one-point)
	H2=half*(one+point)
c
c      write(7,*)'hello H1,H2',h1,h2
c     �κ���ƫ΢��
c
      dndxi(1)=-half
	dndxi(2)=half
c
c      H����
c
c      H(1,1)=H1
c	H(1,3)=H2
c	H(2,2)=H1
c	H(2,4)=H2
c*********************   
      H(1,2)=H1
	H(1,4)=H2
	H(2,1)=H1
	H(2,3)=H2
c      write(7,*)'Starting loop over integration points'
c      write(7,*)'INTP POINT and WEIGHT', IINTP, POINT, WEIGHT
      
      call kaset2(B,2,8) 
	 do i=1,2
	   do j=1,8
	     do k=1,4
	     B(i,j)=B(i,j)+H(i,k)*psi(k,j)
	     enddo
         enddo
       enddo
       
c
c       B ת��
       BT=transpose(B)      
c    
c 
c********������ֵ㴦��ȫ�������µ����λ��DU_cont=[H]*[B]*[U]
c********du_cont(1)Ϊ����λ�ƣ�du_cont(2)Ϊ����λ��
c
      call kaset1(du_cont,2)
      call kaset1(vu_cont,2)
	do i=1,2
	 do j=1,8
	  du_cont(i)=du_cont(i)+B(i,j)*u(j)
        vu_cont(i)=vu_cont(i)+B(i,j)*v(j)
	 enddo
      enddo


c
      
c
c*********�ֲ�����ϵͳ******** 
c   
      X_xi=zero
	Y_xi=zero

      
      do i=1,2
	 X_xi=X_xi+AV_coor(1,i)*dndxi(i)
	 Y_xi=Y_xi+AV_coor(2,i)*dndxi(i)
	enddo
      DETJ=(X_xi**2+Y_xi**2)**0.5d0
c      write(7,*)'dx=',X_xi,AV_coor(1,2),AV_coor(1,1)
c      write(7,*)'dy=',Y_xi,AV_coor(2,2),AV_coor(2,1)
      
c
c****�ֲ�����ʸ��** V_xi(1)=cos V_xi(2)=sin
c
      V_xi(1)=X_xi/(DETJ+1e-18) 
      V_xi(2)=Y_xi/(DETJ+1e-18)
c	
	V_n(1)=-V_xi(2)
	V_n(2)=V_xi(1)
      theta(1,1)=V_xi(1)
	theta(2,1)=-V_n(1)
	theta(1,2)=-V_xi(2)
	theta(2,2)=V_n(2)
      thetat=transpose(theta)
      
          
c  
c     
      call kaset1(DU_loc,2)
      call kaset1(VU_loc,2)
	do i=1,2
	  do j=1,2
	  DU_loc(i)=DU_loc(i)+theta(i,j)*du_cont(j)
        VU_loc(i)=VU_loc(i)+theta(i,j)*vu_cont(j)
	 enddo
      enddo
c
c      write(7,*)'��ת����R=',theta
c      write(7,*)'ȫ�������µ����λ��=',du_cont
c
c

      call law(DU_loc,props,stress,ddsdde,svars,nsvars,iintp,VU_loc,
     1 DTIME,nintp,deln_max,delt_max)
c      
      call kaset2(dd1,2,2)
c*******�նȾ���K=integrate(BT*thetaT*ddsdde*theta*B)
       do i=1,2
	  do j=1,2
	   do k=1,2
	    dd1(i,j)=dd1(i,j)+thetat(i,k)*ddsdde(k,j)
         enddo
	  enddo
	 enddo
c
	call kaset2(d_glob,2,2)
	  do i=1,2
	  do j=1,2
	   do k=1,2
	    d_glob(i,j)=d_glob(i,j)+dd1(i,k)*theta(k,j)
         enddo
	  enddo
	 enddo 
c	    
      call kaset2(A1,8,2)
	  do i=1,8
	  do j=1,2
	   do k=1,2
	    A1(i,j)=A1(i,j)+BT(i,k)*d_glob(k,j)
         enddo
	  enddo
	 enddo 
c
c
      call kaset2(A2,8,8)
	  do i=1,8
	  do j=1,8
	   do k=1,2
	    A2(i,j)=A2(i,j)+A1(i,k)*B(k,j)
         enddo
	  enddo
	 enddo 
c
c     ��Ԫ�նȾ���
      do i=1,8
	  do j=1,8
	   amatrx(i,j)=amatrx(i,j)+width*weight*detJ*A2(i,j)
	  enddo
      enddo
c
c      
      call kaset1(str_glob,2)
	 do i=1,2
	  do j=1,2
	   str_glob(i)=str_glob(i)+thetat(i,j)*stress(j)
	  enddo
	 enddo
c
c
      do i=1,8
	 do j=1,2
	  rhs(i,1)=rhs(i,1)-BT(i,j)*str_glob(j)*width*detJ*weight
	 end do
      enddo
	svars(iintp+nintp)=DU_loc(1)
      svars(iintp+2*nintp)=DU_loc(2)
	svars(iintp+3*nintp)=stress(1)
	svars(iintp+4*nintp)=stress(2)
      
!      if (deln_max.lt.abs(DU_loc(1))) then
!c     1 .and.(strant(1).GT.ln*dn)) then    
!          svars(iintp+5*nintp)=abs(DU_loc(1))
!      endif 

      if (delt_max.lt.abs(DU_loc(2))) then
c     1   .and.(abs(strant(2)).GT.lt*dt)) then
          svars(iintp+6*nintp)=abs(DU_loc(2))
      endif
      !
      NELE=JELEM-ELEMOFFSET
c      write(7,*)'��Ԫ=',NELE
      DO K1=1,NSVINT
       UVAR(NELE,K1,iintp) = SVARS(nintp*(K1-1)+iintp)
      END DO
c
  100 enddo
c
      RETURN
      END
c	
c*****************************************************
      SUBROUTINE law(strant,props,stress,ddsdde,svars,nsvars,iintp,
     1 VU_loc,DTIME,nintp,deln_max,delt_max)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION STRESS(2),props(*),strant(2),ddsdde(2,2),svars(nsvars),
     1 VU_loc(2)
c
      dimension cfull(2,2),cdfull(2,2)
	parameter(zero=0.d0,one=1.d0,two=2.d0,three=3.d0,four=4.d0,
     1 five=5.d0,six=6.d0)
      DOUBLE PRECISION Gn,Gt,Tn_m,Tt_m,alph,beta,ln,lt,th,dn,dt,m,n,
     1    Gam_n,Gam_t,dGnt,dGtn,deln_max,delt_max,kink_point
c******************************************************
c     strant   �������Ӧ��
c  
c     ��֪�Ĳ�������
      E1=props(1)         !�������ն�
	E2=props(2)         !�������ն� 
	SIGI=props(3)       !����ǿ��
	SIGII=props(4)      !����ǿ��
      GIc=props(5)        !modeI ������
	GIIc=props(6)       !modeII ������
	eta=props(7)        !ָ��
      model=props(9)      !1.����.2.petersson.3.CEB-FIP.4.Roesler.5.exponent.6.PPR
c       �����������Ӧ��  
      beta=100            !ָ�����Ĳ���1
      alpha=10.435  !ָ�����Ĳ���2
      dlta_zero=0.8      !�ڶ������ĳ�ʼ���˵����һ�εı�ֵ
      kink_point=0.0025        !ת�۵�λ�������λ�Ƶı�ֵ
c      dummy=0
      multi=1                   !�ڶ����������λ�ƷŴ�ϵ��
      call kaset2(cfull,2,2)
      cfull(1,1)=E1
	cfull(2,2)=E2
c       �����ܵ�Ӧ��
c         
	 dlta=strant(1)**two+strant(2)**two
	 dlta=sqrt(dlta)
	 dlta_max_old=svars(iintp)
	 dlta_max=max(dlta_max_old,dlta)
c       

c
c      ���ݿ�ʼ�ƻ���׼����dlta_o
      

	 cosI=strant(1)/(dlta+1e-15)
       cosII=sqrt(one-cosI**two)



	 dlta_o=(E1*cosI/SIGI)**two+(E2*cosII/SIGII)**two
	 dlta_o=one/sqrt(dlta_o)
c
c      ������ȫ�ƻ���׼����dlta_f
c
      SIGI_Y=E1*dlta_o*cosI
	SIGII_Y=E2*dlta_o*cosII
      dlta_f=(SIGI_Y*cosI/(two*GIc))**eta+
     1	 (SIGII_Y*cosII/(two*GIIc))**eta
      dlta_f=1/dlta_f**(1/eta)
      
      
      
c      Peterssonģ��   

      if (model.eq.two) then
          dlta_wk=(SIGI_Y*cosI/(0.8*GIc))**eta+
     1    (SIGII_Y*cosII/(0.8*GIIc))**eta
          dlta_wk=1/dlta_wk**(1/eta)
          dlta_w1=dlta_o+(dlta_wk-dlta_o)/0.66666667
          dlta_wf=(SIGI_Y*cosI/(3.6*GIc))**eta+
     2    (SIGII_Y*cosII/(3.6*GIIc))**eta
          dlta_wf=1/dlta_wf**(1/eta)
c          
       elseif (model.eq.three) then
          dlta_wf=(SIGI_Y*cosI/(3.5*GIc))**eta+
     1    (SIGII_Y*cosII/(3.5*GIIc))**eta
          dlta_wf=1/dlta_wf**(1/eta)
          dlta_wk=(SIGI_Y*cosI/(2*GIc-0.15*dlta_wf*SIGI_Y))**eta+
     2    (SIGII_Y*cosII/(2*GIIc-0.15*dlta_wf*SIGII_Y))**eta
          dlta_wk=1/dlta_wk**(1/eta)
          dlta_w1=dlta_o+(dlta_wk-dlta_o)/0.85*1
       elseif (model.eq.four) then
           G_f=45*45/E2
           dlta_w1=(SIGI_Y*cosI/(2*G_f))**eta+
     1    (SIGII_Y*cosII/(2*G_f))**eta
           dlta_w1=1/dlta_w1**(1/eta)
           dlta_wk=0.0172
           gamma=(dlta_w1-dlta_wk)/(dlta_w1-dlta_o)
          dlta_wf=(SIGI_Y*cosI*gamma/(2*(GIc-(1-gamma)*G_f)))**eta+
     1    (SIGII_Y*cosII*gamma/(2*(GIIc-(1-gamma)*G_f)))**eta
          dlta_wf=1/dlta_wf**(1/eta)

       end if
c
c      
        
c       
c        �������˱���d
      if (model.eq.one) then
	    if (dlta_max.lt.dlta_o)then
	      d=zero
	     elseif(dlta_max.lt.dlta_f)then
            d=dlta_f*(dlta_max-dlta_o)/(dlta_max*(dlta_f-dlta_o))
	     else
	      d=one
           end if
      elseif (model.eq.two) then
          if (dlta_max.lt.dlta_o)then
	      d=zero
	     elseif((dlta_max.lt.dlta_wk).and.(dlta_max.ge.dlta_o))then
            d=dlta_w1*(dlta_max-dlta_o)/(dlta_max*(dlta_w1-dlta_o))
           elseif((dlta_max.ge.dlta_wk).and.(dlta_max.lt.dlta_wf))then
          d=1-0.33333333*sqrt(SIGI_Y**2+SIGII_Y**2)*(dlta_wf-dlta_max)/
     1      (E2*dlta_max*(dlta_wf-dlta_wk))
           else
            d=one
           end if
       elseif (model.eq.three) then
          if (dlta_max.lt.dlta_o)then
	      d=zero
	     elseif((dlta_max.lt.dlta_wk).and.(dlta_max.ge.dlta_o))then
            d=dlta_w1*(dlta_max-dlta_o)/(dlta_max*(dlta_w1-dlta_o))
           elseif((dlta_max.ge.dlta_wk).and.(dlta_max.lt.dlta_wf))then
            d=1-0.15*sqrt(SIGI_Y**2+SIGII_Y**2)*(dlta_wf-dlta_max)/
     1      (E2*dlta_max*(dlta_wf-dlta_wk))
           else
            d=one
           end if
         elseif (model.eq.four) then
          if (dlta_max.lt.dlta_o)then
	      d=zero
	     elseif((dlta_max.lt.dlta_wk).and.(dlta_max.ge.dlta_o))then
            d=dlta_w1*(dlta_max-dlta_o)/(dlta_max*(dlta_w1-dlta_o))
           elseif((dlta_max.ge.dlta_wk).and.(dlta_max.lt.dlta_wf))then
            d=1-gamma*SIGI_Y*(dlta_wf-dlta_max)/
     1      (E1*dlta_max*(dlta_wf-dlta_wk))
           else
            d=one
           end if
         elseif (model.eq.five) then
	    if (dlta_max.lt.dlta_o)then
	      d=zero
          elseif(dlta_max.lt.dlta_f*kink_point) then
            d=1-(dlta_o/dlta_max)*(1-(1-dexp(-beta*((dlta_max-dlta_o)
     1      /(dlta_f-dlta_o))))/(1-dexp(-beta)))
	     elseif(dlta_max.ge.dlta_f*kink_point.and.dlta_max.lt.dlta_f) then
        d=1-(dlta_o*dlta_zero/(dlta_max))*(1-(1-dexp(-alpha*(((dlta_max)-
     1   dlta_o*dlta_zero)/(dlta_f*multi-dlta_o*dlta_zero))))/(1-dexp(-alpha)))
           end if
         end if 

c     ����Ӧ��
c
      if (model.ne.six) then
	    if (strant(2).ge.zero)then
c����Ϊ����              
	    do i=1,2
	      do j=1,2
	      cdfull(i,j)=(one-d)*cfull(i,j)
	      enddo
          enddo
	     do i=1,2
	     stress(i)=zero
	      do j=1,2
                    stress(i)=stress(i)+cdfull(i,j)*strant(j)
            end do
           end do 
	    else
	    do i=1,2
	      do j=1,2
	      cdfull(i,j)=(one-d)*cfull(i,j)
	      enddo
          enddo
	     cdfull(1,1)=E1
	     stress(1)=E1*strant(1)
	     stress(2)=cdfull(2,2)*strant(2)
          end if
        end if
      

c     �������ߵ��Ծ���
c
      if (model.eq.one.or.model.eq.five) then
          h=dlta_f*dlta_o/(dlta_f-dlta_o)
      elseif (model.eq.two.or.model.eq.three.or.model.eq.four)then
          if ((dlta_max.lt.dlta_wk).and.(dlta_max.ge.dlta_o))then
              h=dlta_w1*dlta_o/(dlta_w1-dlta_o)
          elseif((dlta_max.ge.dlta_wk).and.(dlta_max.lt.dlta_wf))then
              h=dlta_wf*dlta_o/(dlta_wf-dlta_o)
          end if
      end if
      h=h/(dlta+1e-15)**three
      if (model.ne.six) then
	    if(d.gt.zero.and.d.lt.one.and.dlta.gt.dlta_max_old)then
	      if(strant(i).ge.zero) then
            ddsdde(1,1)=cdfull(1,1)-h*E1*strant(1)**two
c
c
	      ddsdde(1,2)=cdfull(1,2)-h*E1*strant(1)*strant(2)
	      ddsdde(2,1)=cdfull(2,1)-h*E2*strant(1)*strant(2)
	      ddsdde(2,2)=cdfull(2,2)-h*E2*strant(2)**two         
	      elseif(strant(1).lt.zero)then
	      ddsdde(1,1)=E1
	      ddsdde(1,2)=zero
	      ddsdde(2,1)=zero
	      ddsdde(2,2)=cdfull(2,2)-h*E2*strant(2)**two
            endif
	      else
	      do i=1,2
	        do j=1,2
	        ddsdde(i,j)=cdfull(i,j)
	        enddo
            enddo
            endif
          endif
          
c       PPRģ�Ͳ�������
c     Gn,Gt: �������������
c     dn,dt: ���շ��������ƻ�λ��
c     Tn_m, Tt_m  :���������ճ����
c     deln_max,delt_max:���ع����е�������   
c     ln,lt: ��ʼб������ 
c       ������� & ��ʼ��
!      if(model.eq.six)then
!        Gn = 500
!        Gt = 16.5
!        Tn_m = 5300
!        Tt_m = 5.3
!        alph = 5
!        beta = 5
!        ln = 1
!        lt = 0.01
!c        th = 1
!c       ȷ��PPR����
!        m = (alph-1)*alph*ln**2/(1-alph*ln**2)
!        n = (beta-1)*beta*lt**2/(1-beta*lt**2)
!        dn = alph*Gn/(m*Tn_m)*(1-ln)**(alph-1)
!     1      *(alph/m*ln+1)**(m-1)*(alph+m)*ln
!        dt = beta*Gt/(n*Tt_m)*(1-lt)**(beta-1)
!     1      *(beta/n*lt+1)**(n-1)*(beta+n)*lt
!        if (Gt.gt.Gn) then
!            dGnt = 0
!            dGtn = Gt-Gn
!        elseif (Gt.Lt.Gn) then
!            dGtn = 0
!            dGnt = Gn-Gt
!        else
!            dGtn = 0
!            dGnt = 0
!        endif
!        if (Gn.eq.Gt) then
!            Gam_n = -Gn*(alph/m)**m
!            Gam_t = (beta/n)**n
!        else
!            Gam_n = (-Gn)**(dGnt/(Gn-Gt))*(alph/m)**m
!            Gam_t = (-Gt)**(dGtn/(Gt-Gn))*(beta/n)**n
!        endif
!c======================================================================
!c = ճ��ǣ�������ϵ====================================================
!c = ����λ������³�������λ�ƶ�Ҫ����
!c = deln,delt��ȷ     
!        deln = abs(strant(1))
!        delt = abs(strant(2))
!        if (strant(2).ge.0) then 
!            sign_dt = 1
!        else
!            sign_dt=-1
!        endif
!        Tn = 0
!c   ���㷨��ǣ����Tn=stress(1)
!        if (deln.lt.0) then
!            deln = 0
!        elseif ((deln.ge.dn).or.(delt.ge.dt)) then 
!            Tn= 0
!        elseif  (deln.ge.deln_max) then
!            Tn = (Gam_t*(1-delt/dt)**beta*(delt/dt+n/beta)**n+dGtn)*
!     1      Gam_n/dn*(m*(1-deln/dn)**alph*(m/alph+deln/dn)**(m-1)-alph
!     2      *(1-deln/dn)**(alph-1)*(m/alph+deln/dn)**m)
!        else
!            Tn = (Gam_t*(1-delt/dt)**beta*(delt/dt+n/beta)**n+dGtn)*
!     1      Gam_n/dn*(m*(1-deln_max/dn)**alph*(m/alph+deln_max/dn)**
!     2       (m-1)-alph*(1-deln_max/dn)**(alph-1)*(m/alph+deln_max/dn)
!     3       **m)*deln/deln_max
!        endif
!c   ��������ǣ����Tt=stress(2)
!c   ����λ��������λ�ƶ��������ֵ�����     
!        if ((deln.ge.dn).or.(delt.ge.dt)) then
!            Tt = 0
!        elseif (delt.ge.delt_max) then 
!            Tt = (Gam_n*(1-deln/dn)**alph*(deln/dn+m/alph)**m+dGnt)*
!     1      Gam_t/dt*(n*(1-delt/dt)**beta*(n/beta+delt/dt)**(n-1)-beta
!     2      *(1-delt/dt)**(beta-1)*(n/beta+delt/dt)**n)
!        else
!            Tt = (Gam_n*(1-deln/dn)**alph*(deln/dn+m/alph)**m+dGnt)*
!     1      Gam_t/dt*(n*(1-delt_max/dt)**beta*(n/beta+delt_max/dt)**
!     2      (n-1)-beta*(1-delt_max/dt)**(beta-1)*(n/beta+delt_max/dt)
!     3      **n)*delt/delt_max
!        endif
!c     ����ճ������Ϊ  
!c     (1)�Ӵ�
!c     ������λ�ƴ���0����Ӵ�
!        if (deln.lt.0) then
!            ddsdde(1,1) = -Gam_n/dn**2*(m/alph)**(m-1)*(alph+m)*
!     1  (Gam_t*(n/beta)**n + dGtn)
!            ddsdde(1,2) = 0
!            stress(1) = ddsdde(1,1)*abs(strant(1))
!c     ����������λ�ƽ�С�ڷ�������λ�����ֵ���ҷ���ǣ������һ��ֵ����            
!        else if ((deln.lt.dn).and.(delt.lt.dt).and.(Tn.ge.-1.0e-5)) then
!            stress(1) = Tn
!c     (2)��
!c     ������λ�ƴ��ڼ�����ʷ��������λ�ƣ�����
!        if (deln.ge.deln_max) then
!            ddsdde(1,1) = 
!     1  (Gam_t*(1-delt/dt)**beta*(delt/dt+n/beta)**n+dGtn)*
!     2  Gam_n/dn**2*
!     3  ((1-deln/dn)**(alph-2)*(alph-1)*alph*(deln/dn+m/alph)**m-
!     4  2*(1-deln/dn)**(alph-1)*alph*(deln/dn+m/alph)**(m-1)*m+
!     5  (1-deln/dn)**alph*(deln/dn+m/alph)**(m-2)*(m-1)*m)
!            ddsdde(1,2) = 
!     1  (Gam_t/dt*(-(1-delt/dt)**(beta-1)*beta*(delt/dt+n/beta)**n+
!     2   (1-delt/dt)**beta*(delt/dt+n/beta)**(n-1)*n)*sign_dt*
!     2  Gam_n/dn*(-(1-deln/dn)**(alph-1)*alph*(deln/dn+m/alph)**m+
!     5  (1-deln/dn)**alph*(deln/dn+m/alph)**(m-1)*m))
!c     (3)ж��/�ؼ������
!c     ������λ��С�ڼ�����ʷ��������λ�ƣ���ж��          
!        else
!            ddsdde(1,1) = 
!     1  (Gam_t*(1-delt/dt)**beta*(delt/dt+n/beta)**n+dGtn)*
!     2  Gam_n/dn*((1-deln_max/dn)**alph*(deln_max/dn+m/alph)**(m-1)*m
!     4  -(1-deln_max/dn)**(alph-1)*alph*(deln_max/dn+m/alph)**m)/deln_max
!            ddsdde(1,2) = 
!     1  Gam_t/dt*(-(1-delt/dt)**(beta-1)*beta*(delt/dt+n/beta)**n+
!     2   (1-delt/dt)**beta*(delt/dt+n/beta)**(n-1)*n)*sign_dt*
!     2  Gam_n/dn*(m*(1-deln_max/dn)**alph*(deln_max/dn+m/alph)**(m-1)-
!     5  alph*(1-deln_max/dn)**(alph-1)*(m/alph+deln_max/dn)**m)*deln/deln_max
!      endif
!c     (4)��ȫ�ƻ�����
!c     ��������������ֵ���ƻ�     
!      else
!          stress(1) = 0
!          ddsdde(1,1) = 0
!          ddsdde(1,2) = 0
!      endif
!c    ����ճ������Ϊ    
!      if ((delt.lt.dt).and.(deln.lt.dn).and.(Tt.ge.-1.0e-5)) then
!          stress(2) = Tt*sign_dt
!c     (1)��
!c     ������λ�ƴ������������ʷ��������λ�ƣ�����          
!      if (delt.ge.delt_max) then
!              ddsdde(2,2) = 
!     1   (Gam_n*(1-deln/dn)**alph*(deln/dn+m/alph)**m+dGnt)*
!     2  Gam_t/dt**2*
!     3  ((1-delt/dt)**(beta-2)*(beta-1)*beta*(delt/dt+n/beta)**n-
!     4  2*(1-delt/dt)**(beta-1)*beta*(delt/dt+n/beta)**(n-1)*n+
!     5  (1-delt/dt)**beta*(delt/dt+n/beta)**(n-2)*(n-1)*n)
!              ddsdde(2,1) =
!     1   Gam_t/dt*(-(1-delt/dt)**(beta-1)*beta*(delt/dt+n/beta)**n+
!     2   (1-delt/dt)**beta*(delt/dt+n/beta)**(n-1)*n)*sign_dt*
!     2  Gam_n/dn*(-(1-deln/dn)**(alph-1)*alph*(deln/dn+m/alph)**m+
!     5  (1-deln/dn)**alph*(deln/dn+m/alph)**(m-1)*m)
!c     (2)ж��/�ؼ������
!c     ������λ��С�ڼ�����ʷ��������λ�ƣ���ж��    
!      else
!            ddsdde(2,2) = 
!     1  (Gam_n*(1-deln/dn)**alph*(deln/dn+m/alph)**m+dGnt)*
!     2  Gam_t/dt*(n*(1-delt_max/dt)**beta*(delt_max/dt+n/beta)**(n-1)
!     4  -beta*(1-delt_max/dt)**(beta-1)*(delt_max/dt+n/beta)**n)/delt_max
!            ddsdde(2,1) = 
!     1   Gam_n/dn*(-(1-deln/dn)**(alph-1)*alph*(deln/dn+m/alph)**m+
!     2   (1-deln/dn)**alph*(deln/dn+m/alph)**(m-1)*m)*sign_dt*
!     2  Gam_t/dt*(n*(1-delt_max/dt)**beta*(delt_max/dt+n/beta)**(n-1)-
!     5  beta*(1-delt_max/dt)**(beta-1)*(n/beta+delt_max/dt)**n)*delt/delt_max
!      endif
!c     (3)��ȫ�ƻ�����
!c     ��������������ֵ���ƻ�     
!      else
!          stress(2) = 0
!          ddsdde(2,2) = 0
!          ddsdde(2,1) = 0
!      endif
!      if (ddsdde(1,2).ne.ddsdde(2,1)) then 
!          ddsdde(2,1) = 0.5*(ddsdde(1,2)+ddsdde(2,1))
!          ddsdde(1,2) = ddsdde(2,1)
!      endif 
!
!      endif

        
c
c     ճ������
C        ZETA is the fictitious viscosity used to regularize the instability problem. 
      ZETA=0.00004D0
      stress(2)=stress(2)+ZETA*PROPS(4)*(one-d)*VU_loc(2)/dlta_o
      ddsdde(2,2)=ddsdde(2,2)+ZETA*PROPS(4)*(one-d)/dlta_o/DTIME
c      stress(1)=stress(1)+ZETA*PROPS(3)*(one-d)*VU_loc(1)/dlta_o
c      ddsdde(1,1)=ddsdde(1,1)+ZETA*PROPS(3)*(one-d)/dlta_o/DTIME

        
c
      svars(iintp)=dlta_max
c     

      svars(iintp+5*nintp)=d

c      

      RETURN
      END
      
      
c
c****************************************************************
      subroutine kaset1(dmatrix,idimx)
	include 'ABA_PARAM.inc'
	parameter(zero=0.0d0)
	dimension dmatrix(idimx)
	 do i=1,idimx
	  dmatrix(i)=zero
	 enddo
	return
	end
c
c*************************************************
c	
	subroutine kaset2(dmatrix,idimx,idimy)
      include 'ABA_PARAM.inc'
	parameter(zero=0.0d0)
	dimension dmatrix(idimx,idimy)
	 do i=1,idimx
	  do j=1,idimy
	   dmatrix(i,j)=zero
	  enddo
	 enddo
	return
      end
      
      
      
      SUBROUTINE UMAT(STRESS, STATEV, DDSDDE, SSE, SPD, SCD, RPL,
     1 DDSDDT, DRPLDE, DRPLDT, STRAN, DSTRAN, TIME, DTIME, TEMP,
     2 DTEMP, PREDEF, DPRED, CMNAME, NDI, NSHR, NTENS, NSTATV,
     3 PROPS, NPROPS, COORDS, DROT, PNEWDT, CELENT, DFGRD0,
     4 DFGRD1, NOEL, NPT, LAYER, KSPT, KSTEP, KINC)
      INCLUDE 'ABA_PARAM.INC'
      CHARACTER*80 CMNAME
      PARAMETER(NINT=2.d0, NSTV=7.d0, NELEMENT=25306.d0, ELEMOFFSET=83200.d0)
      DIMENSION STATEV(NSTATV)
      INTEGER NELEMAN, K1
      COMMON/KUSER/UVAR(NELEMENT,NSTV,NINT)
      NELEMAN=NOEL-ELEMOFFSET-NELEMENT
c      write(7,*)'NELEMAN ��Ԫ=',NELEMAN
          DO K1=1,NSTV
          STATEV(K1)=UVAR(NELEMAN,K1,NPT)
          END DO
      RETURN
      end