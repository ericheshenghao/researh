def Macro8():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    
    name = 'TPB-2530-1%-orientation'
    s1 = mdb.models[name].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(10.0, 0.0))
    p = mdb.models[name].Part(name='Part-2', 
        dimensionality=TWO_D_PLANAR, type=DISCRETE_RIGID_SURFACE)
    p = mdb.models[name].parts['Part-2']
    p.BaseWire(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models[name].parts['Part-2']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models[name].sketches['__profile__']
    a = mdb.models[name].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    a1 = mdb.models[name].rootAssembly
    p = mdb.models[name].parts['Part-2']
    a1.Instance(name='Part-2-1', part=p, dependent=ON)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=762.223, 
        farPlane=935.776, width=569.473, height=209.992, viewOffsetX=54.6988, 
        viewOffsetY=17.14)
    a1 = mdb.models[name].rootAssembly
    a1.translate(instanceList=('Part-2-1', ), vector=(200.0, 110.0, 0.0))
    a1 = mdb.models[name].rootAssembly
    p = mdb.models[name].parts['Part-2']
    a1.Instance(name='Part-2-2', part=p, dependent=ON)
    a1 = mdb.models[name].rootAssembly
    a1.translate(instanceList=('Part-2-2', ), vector=(50.0, -10.0, 0.0))
    session.viewports['Viewport: 1'].view.setValues(nearPlane=725.463, 
        farPlane=995.002, width=985.083, height=363.247, viewOffsetX=71.3468, 
        viewOffsetY=-3.85389)
    a1 = mdb.models[name].rootAssembly
    a1.LinearInstancePattern(instanceList=('Part-2-2', ), direction1=(1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1=300.0, 
        spacing2=20.0)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=763.935, 
        farPlane=956.53, width=632.321, height=233.166, viewOffsetX=91.8074, 
        viewOffsetY=15.7017)
    p1 = mdb.models[name].parts['Part-2']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    p = mdb.models[name].parts['Part-2']
    v2, e1, d1, n1 = p.vertices, p.edges, p.datums, p.nodes
    p.ReferencePoint(point=p.InterestingPoint(edge=e1.findAt(coordinates=(0.0, 
        10.0, 0.0)), rule=CENTER))