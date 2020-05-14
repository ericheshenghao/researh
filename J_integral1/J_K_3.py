
import numpy as np
def J_integral(ue,ve,xe,ye,qe,xcenter,ycenter,E,mu,G,kapa):
	ue=np.matrix(ue); # element 1 direction displacement (1x4)
	ve=np.matrix(ve); # element 2 direction displacement (1x4)
	xe=np.matrix(xe); # element 1 direction coordinates  (1x4) 
	ye=np.matrix(ye); # element 2 direction coordinates  (1x4)
	qe=np.matrix(qe); # element q function value at element node (1x4)
	
	rs=np.matrix([[-1.0/np.sqrt(3),1.0/np.sqrt(3),1.0/np.sqrt(3),-1.0/np.sqrt(3)],[-1.0/np.sqrt(3),-1.0/np.sqrt(3),1.0/np.sqrt(3),1.0/np.sqrt(3)]]) # integral point's position
	
	const = E/(1.0-mu**2.0)
	Ce = const*np.matrix([[1.0,mu,0.0],[mu,1.0,0.0],[0.0,0.0,(1.0-mu)/2.0]]) # elastic matrix
	Je=0.0
	JmixI=0.0
	JmixII=0.0
	JauxI=0.0
	JauxII=0.0
	for ip in range(0,4): # loop over 4 integral point
		r = rs[0,ip]
		s = rs[1,ip]
		N = np.matrix([(1.0-r)*(1.0-s)/4.0,(1.0+r)*(1.0-s)/4.0,(1.0+r)*(1.0+s)/4.0,(1.0-r)*(1.0+s)/4.0])  # element shape function
		Nr = np.matrix([-(1.0-s)/4.0, (1.0-s)/4.0, (1.0+s)/4.0, -(1.0+s)/4.0])                    # the 1-direction derivative of shape function 
		Ns = np.matrix([-(1.0-r)/4.0, -(1.0+r)/4.0, (1.0+r)/4.0, (1.0-r)/4.0])                    # the 2-direction derivative of shape funciton
		xr = (Nr*xe.H)[0,0]
		xs = (Ns*xe.H)[0,0]
		yr = (Nr*ye.H)[0,0]
		ys = (Ns*ye.H)[0,0]                # d(x,y)/d(ksi,eta)
		detJe = (xr*ys-xs*yr)                   # element Jaucobi det at integral point 
		Nx = (ys*Nr-yr*Ns)/detJe  # dN/dx
		Ny = (-xs*Nr+xr*Ns)/detJe # dN/dy
		
		# ==========================Original Field=======================
		ux = (Nx*ue.H)[0,0]              # du/dx
		uy = (Ny*ue.H)[0,0]              # du/dy
		vx = (Nx*ve.H)[0,0]              # dv/dx
		vy = (Ny*ve.H)[0,0]              # dv/dy
		qx = (Nx*qe.H)[0,0]              # dq/dx for all Field
		qy = (Ny*qe.H)[0,0]              # dq/dy for all Field
		exx = ux		
		eyy = vy
		exy = uy+vx
		ee = np.matrix([exx,eyy,exy])
		ss = (Ce*ee.H).H
		sxx=ss[0,0]
		syy=ss[0,1]
		sxy=ss[0,2]
		
		# ==========================Integral Point Locations=======================
		xq = (N*xe.H)[0,0]
		yq = (N*ye.H)[0,0]         # integral point coordinates 
		rr = np.sqrt(((xq- xcenter)**2.0)+((yq- ycenter)**2.0))
		theta = np.arctan2((yq- ycenter),(xq- xcenter))
		
		# ==========================I Type Auxiliary Field=======================
		ssI = (1.0/np.sqrt(2*np.pi*rr))*\
		np.matrix([(1.0-np.sin(theta/2)*np.sin(theta*3/2))*np.cos(theta/2),(1.0+np.sin(theta/2)*np.sin(theta*3/2))*np.cos(theta/2),(np.sin(theta/2)*np.cos(theta*3/2))*np.cos(theta/2)])
		sxxI=ssI[0,0]
		syyI=ssI[0,1]
		sxyI=ssI[0,2]
		uxI = (1.0/4.0/G/np.sqrt(2*np.pi*rr))*((np.cos(theta/2))*(8*((np.cos(theta/2))**4)-10*((np.cos(theta/2))**2)+kapa+1))
		vxI = (1.0/4.0/G/np.sqrt(2*np.pi*rr))*((np.sin(theta/2))*(8*((np.cos(theta/2))**4)- 6*((np.cos(theta/2))**2)-kapa-1))
		eeI = np.matrix([ (sxxI -mu*syyI)/E,(syyI- mu*sxxI)/E,sxyI/G])
		exxI=eeI[0,0]
		eyyI=eeI[0,1]
		exyI=eeI[0,2]
		
		# ==========================II Type Auxiliary Field=======================
		ssII = (1.0/np.sqrt(2*np.pi*rr))*\
		np.matrix([ -np.sin(theta/2)*(2-np.cos(theta/2)*np.cos(theta*3/2)),np.sin(theta/2)*np.cos(theta/2)*np.cos(theta*3/2),np.cos(theta/2)*(1-np.sin(theta/2)*np.sin(theta*3/2))])
		sxxII=ssII[0,0]
		syyII=ssII[0,1]
		sxyII=ssII[0,2]       
		uxII = (-1.0/4/G/np.sqrt(2*np.pi*rr))*((np.sin(theta/2))*(8*((np.cos(theta/2))**4)-6*((np.cos(theta/2))**2)+kapa+1))
		vxII = (1.0/4/G/np.sqrt(2*np.pi*rr))*((np.cos(theta/2))*(8*((np.cos(theta/2))**4)-10*((np.cos(theta/2))**2)-kapa+3));
		eeII = np.matrix([ (sxxII -mu*syyII)/E,(syyII- mu*sxxII)/E,sxyII/G])
		exxII=eeII[0,0]
		eyyII=eeII[0,1]
		exyII=eeII[0,2]
		
		# ==========================II Type Mixed Field=======================
		sxxmixI = sxx+sxxI
		syymixI = syy+syyI
		sxymixI = sxy+sxyI
		ssmixI = np.matrix([sxxmixI,syymixI,sxymixI])
		exxmixI = exx+exxI
		eyymixI = eyy+eyyI
		exymixI = exy+exyI
		eemixI = np.matrix([exxmixI,eyymixI,exymixI])
		uxmixI = ux+uxI
		vxmixI = vx+vxI
		
		# ==========================II Type Mixed Field=======================
		sxxmixII = sxx+sxxII
		syymixII = syy+syyII
		sxymixII = sxy+sxyII
		ssmixII = np.matrix([sxxmixII,syymixII,sxymixII])
		exxmixII = exx+exxII
		eyymixII = eyy+eyyII
		exymixII = exy+exyII
		eemixII = np.matrix([exxmixII,eyymixII,exymixII])
		uxmixII = ux+uxII
		vxmixII = vx+vxII
		
		# ==========================Original Field J Integral=======================
		w = (0.5*ss*ee.H)[0,0]
		Je = Je+((sxx*ux+sxy*vx-w)*qx+(sxy*ux+syy*vx)*qy)*detJe
		
		# ==========================I Type Mixed Field J Integral=======================
		wmixI = (0.5*ssmixI*eemixI.H)[0,0]
		JmixI = JmixI+((sxxmixI*uxmixI+sxymixI*vxmixI-wmixI)*qx+(sxymixI*uxmixI+syymixI*vxmixI)*qy)*detJe
		
		# ==========================II Type Mixed Field J Integral=======================
		wmixII = (0.5*ssmixII*eemixII.H)[0,0]
		JmixII = JmixII+((sxxmixII*uxmixII+sxymixII*vxmixII-wmixII)*qx+(sxymixII*uxmixII+syymixII*vxmixII)*qy)*detJe
		
		# ==========================I Type Auxiliary Field J Integral=======================
		wauxI = (0.5*ssI*eeI.H)[0,0]
		JauxI = JauxI+((sxxI*uxI+sxyI*vxI-wauxI)*qx+(sxyI*uxI+syyI*vxI)*qy)*detJe
		
		# ==========================II Type Auxiliary Field J Integral=======================
		wauxII = (0.5*ssII*eeII.H)[0,0]
		JauxII = JauxII+((sxxII*uxII+sxyII*vxII-wauxII)*qx+(sxyII*uxII+syyII*vxII)*qy)*detJe
		
	Ie1 = JmixI - Je - JauxI
	Ie2 = JmixII - Je - JauxII
	return [ Je,Ie1,Ie2 ]

from odbAccess import *
def post(StepIndex,TotalFrames,Jr,xcentero,ycentero,xvertexo,yvertexo,problemtype,enter,fileName,centernode,vertexnode):
	odb = openOdb(fileName)
	try:
		if not enter:
			xcentero = centernode.coordinates[0]
			ycentero = centernode.coordinates[1]
			xvertexo = vertexnode.coordinates[0]
			yvertexo = vertexnode.coordinates[1]
	except:
		pass

	beta = np.arctan2((ycentero- yvertexo),(xcentero- xvertexo))
	xcenter = xcentero*np.cos(beta) + ycentero*np.sin(beta)
	ycenter = -xcentero*np.sin(beta) + ycentero*np.cos(beta)

	step1 = odb.steps.values()[StepIndex]

	if TotalFrames != -1:
		for frameno in range(0,TotalFrames):
			lastFrame = step1.frames[frameno]
			displacement = lastFrame.fieldOutputs['U'].values
			totalnode=odb.rootAssembly.instances['PART-1-PICKGEOEDGES-1'].nodes
			totalele =odb.rootAssembly.instances['PART-1-PICKGEOEDGES-1'].elementSets['BASEELEMENTS'].elements
			mat = odb.materials
			E = mat['POLARISCDP_1'].elastic.table[0][0]
			mu = mat['POLARISCDP_1'].elastic.table[0][1]
			G = E/2.0/(1.0+mu)
			kapa = (3.0-mu)/(1.0+mu)
			if problemtype=='plane strain':
				E = E/(1.0-mu**2.0)
				mu = mu/(1.0-mu)
				G = E/2.0/(1.0+mu)
				kapa = 3.0-4.0*mu
	
			J = 0.0
			I1 = 0.0
			I2 = 0.0
			eleee=[]
			for ele in totalele:
				xe = [0.0,0.0,0.0,0.0]
				ye = [0.0,0.0,0.0,0.0]
				dis = [0.0,0.0,0.0,0.0]
				ue = [0.0,0.0,0.0,0.0]
				ve = [0.0,0.0,0.0,0.0]
				qe = [0.0,0.0,0.0,0.0]
				for i in range(0,4):
					xeo = totalnode[ ele.connectivity[i]-1 ].coordinates[0]
					yeo = totalnode[ ele.connectivity[i]-1 ].coordinates[1]
					xe[i] = xeo*np.cos(beta) + yeo*np.sin(beta)
					ye[i] = -xeo*np.sin(beta) + yeo*np.cos(beta)
					dis[i] = np.sqrt((xe[i]- xcenter)**2.0+(ye[i]- ycenter)**2.0)-Jr
				pass
				if dis[0]*dis[1]<0.0 or dis[0]*dis[2]<0.0 or dis[0]*dis[3]<0.0:
					for i in range(0,4):
						for v in displacement:
							if v.nodeLabel==ele.connectivity[i]:
								ueo = v.data[0]
								veo = v.data[1]
								ue[i] = ueo*np.cos(beta) + veo*np.sin(beta)
								ve[i] = -ueo*np.sin(beta) + veo*np.cos(beta)
								if dis[i]<0.0:
									qe[i] = 1.0

					[ Je,Ie1,Ie2 ] = J_integral(ue,ve,xe,ye,qe,xcenter,ycenter,E,mu,G,kapa)
  
					if Je>0.0:
						#print('Element = %f'%(ele.label))
						#print('xe = [%f, %f, %f, %f]'%(xe[0],xe[1],xe[2],xe[3])) 
						#print('ye = [%f, %f, %f, %f]'%(ye[0],ye[1],ye[2],ye[3]))
						#print('ue = [%f, %f, %f, %f]'%(ue[0],ue[1],ue[2],ue[3]))
						#print('ve = [%f, %f, %f, %f]'%(ve[0],ve[1],ve[2],ve[3]))
						#print('dis = [%f, %f, %f, %f]'%(dis[0],dis[1],dis[2],dis[3]))
						#print('qe = [%f, %f, %f, %f]'%(qe[0],qe[1],qe[2],qe[3]))    
						#print('Je=%f'%Je) 
						#print('Ie1=%f'%Ie1) 
						#print('Ie2=%f'%Ie2)
						#print('          ')

						J = J + Je
						I1 = I1 + Ie1
						I2 = I2 + Ie2
						eleee.append(ele.label)

			#print('Integral radius : %f'%Jr)

			#print('(X_Tip,Y_Tip) = (%f,%f), (X_Vertex,Y_Vertex) = (%f,%f)'%(xcentero,ycentero,xvertexo,yvertexo))

			#print('Beta = %f Degree'%(beta*180/np.pi))

			#print('E = %f , mu = %f '%(E, mu))

			#print('I1 = %f , I2 = %f , J = %f '%(I1, I2, J))

			print('Frame Index = %f , KI = %f , KII = %f , K = %f '%(frameno,I1*E/2,I2*E/2,np.sqrt(J*E)))
	
			#print(eleee)

	'''
	if TotalFrames == -1:
		lastFrame = step1.frames[-1]
		displacement = lastFrame.fieldOutputs['U'].values
		totalnode=odb.rootAssembly.instances['PART-1-1'].nodes
		totalele = odb.rootAssembly.instances['PART-1-1'].elements
		mat = odb.materials
		E = mat['MATERIAL-1'].elastic.table[0][0]
		mu = mat['MATERIAL-1'].elastic.table[0][1]
		G = E/2.0/(1.0+mu)
		kapa = (3.0-mu)/(1.0+mu)
		if problemtype=='plane strain':
			E = E/(1.0-mu**2.0)
			mu = mu/(1.0-mu)
			G = E/2.0/(1.0+mu)
			kapa = 3.0-4.0*mu
	
		J = 0.0
		I1 = 0.0
		I2 = 0.0
		eleee=[]
		for ele in totalele:
			xe = [0.0,0.0,0.0,0.0]
			ye = [0.0,0.0,0.0,0.0]
			dis = [0.0,0.0,0.0,0.0]
			ue = [0.0,0.0,0.0,0.0]
			ve = [0.0,0.0,0.0,0.0]
			qe = [0.0,0.0,0.0,0.0]
			for i in range(0,4):
				xeo = totalnode[ ele.connectivity[i]-1 ].coordinates[0]
				yeo = totalnode[ ele.connectivity[i]-1 ].coordinates[1]
				xe[i] = xeo*np.cos(beta) + yeo*np.sin(beta)
				ye[i] = -xeo*np.sin(beta) + yeo*np.cos(beta)
				dis[i] = np.sqrt((xe[i]- xcenter)**2.0+(ye[i]- ycenter)**2.0)-Jr
			pass
			if dis[0]*dis[1]<0.0 or dis[0]*dis[2]<0.0 or dis[0]*dis[3]<0.0:
				for i in range(0,4):
					for v in displacement:
						if v.nodeLabel==ele.connectivity[i]:
							ueo = v.data[0]
							veo = v.data[1]
							ue[i] = ueo*np.cos(beta) + veo*np.sin(beta)
							ve[i] = -ueo*np.sin(beta) + veo*np.cos(beta)
							if dis[i]<0.0:
								qe[i] = 1.0

				[ Je,Ie1,Ie2 ] = J_integral(ue,ve,xe,ye,qe,xcenter,ycenter,E,mu,G,kapa)
  
				if Je>0.0:
					#print('Element = %f'%(ele.label))
					#print('xe = [%f, %f, %f, %f]'%(xe[0],xe[1],xe[2],xe[3])) 
					#print('ye = [%f, %f, %f, %f]'%(ye[0],ye[1],ye[2],ye[3]))
					#print('ue = [%f, %f, %f, %f]'%(ue[0],ue[1],ue[2],ue[3]))
					#print('ve = [%f, %f, %f, %f]'%(ve[0],ve[1],ve[2],ve[3]))
					#print('dis = [%f, %f, %f, %f]'%(dis[0],dis[1],dis[2],dis[3]))
					#print('qe = [%f, %f, %f, %f]'%(qe[0],qe[1],qe[2],qe[3]))    
					#print('Je=%f'%Je) 
					#print('Ie1=%f'%Ie1) 
					#print('Ie2=%f'%Ie2)
					#print('          ')

					J = J + Je
					I1 = I1 + Ie1
					I2 = I2 + Ie2
					eleee.append(ele.label)

		#print('Integral radius : %f'%Jr)

		#print('(X_Tip,Y_Tip) = (%f,%f), (X_Vertex,Y_Vertex) = (%f,%f)'%(xcentero,ycentero,xvertexo,yvertexo))

		#print('Beta = %f Degree'%(beta*180/np.pi))

		#print('E = %f , mu = %f '%(E, mu))

		#print('I1 = %f , I2 = %f , J = %f '%(I1, I2, J))

		print('KI = %f , KII = %f , K = %f '%(I1*E/2,I2*E/2,np.sqrt(J*E)))
	
		#print(eleee)
		'''

def main_Jintegral(StepIndex,TotalFrames,Jr,xcentero,ycentero,xvertexo,yvertexo,problemtype,enter,fileName,centernode=None,vertexnode=None):
	post(StepIndex,TotalFrames,Jr,xcentero,ycentero,xvertexo,yvertexo,problemtype,enter,fileName,centernode,vertexnode)