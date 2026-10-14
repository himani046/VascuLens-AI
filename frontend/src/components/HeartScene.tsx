import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html, useGLTF } from '@react-three/drei'
import { Suspense, useMemo, useRef } from 'react'
import * as THREE from 'three'

type ID = 'LAD' | 'LCX' | 'RCA'
type Vessel = { key: string; id: ID; name: string; points: [number, number, number][]; branch?: boolean }
const vessels: Vessel[] = [
  { key: 'lad-main', id: 'LAD', name: 'Left anterior descending', points: [[0.02,.63,.37],[.12,.46,.48],[.16,.22,.49],[.10,-.12,.43],[-.04,-.52,.27]] },
  { key: 'lad-diagonal-1', id: 'LAD', name: 'First diagonal branch', branch: true, points: [[.14,.33,.48],[.30,.23,.43],[.37,.04,.32]] },
  { key: 'lad-diagonal-2', id: 'LAD', name: 'Second diagonal branch', branch: true, points: [[.12,.10,.45],[.27,-.02,.38],[.31,-.20,.29]] },
  { key: 'lad-septal-1', id: 'LAD', name: 'Septal branch', branch: true, points: [[.13,.19,.48],[.04,.05,.46],[-.01,-.12,.39]] },
  { key: 'lcx-main', id: 'LCX', name: 'Left circumflex', points: [[.02,.63,.37],[-.17,.53,.41],[-.36,.36,.35],[-.48,.12,.23],[-.38,-.16,.13]] },
  { key: 'lcx-om-1', id: 'LCX', name: 'Obtuse marginal branch', branch: true, points: [[-.34,.34,.35],[-.23,.18,.39],[-.13,-.02,.32]] },
  { key: 'lcx-om-2', id: 'LCX', name: 'Second marginal branch', branch: true, points: [[-.43,.18,.28],[-.34,.00,.25],[-.23,-.18,.19]] },
  { key: 'rca-main', id: 'RCA', name: 'Right coronary artery', points: [[.08,.55,.34],[.31,.48,.36],[.49,.27,.29],[.47,.02,.23],[.31,-.25,.18]] },
  { key: 'rca-marginal', id: 'RCA', name: 'Right marginal branch', branch: true, points: [[.46,.10,.25],[.39,-.08,.24],[.27,-.22,.19]] },
  { key: 'rca-pda', id: 'RCA', name: 'Posterior descending branch', branch: true, points: [[.31,-.24,.18],[.12,-.36,.22],[-.08,-.45,.18],[-.20,-.47,.12]] },
]
const riskColor = (p?: number) => p === undefined ? '#b85e69' : p >= .65 ? '#ed4857' : p >= .35 ? '#e6a23c' : '#19a783'


function AnatomicalHeartModel() {
  const { scene } = useGLTF('/models/anatomical_heart_-_codominance.glb')
  const prepared = useMemo(() => {
    const clone = scene.clone(true)
    clone.updateMatrixWorld(true)
    const bounds = new THREE.Box3().setFromObject(clone)
    const center = bounds.getCenter(new THREE.Vector3())
    const size = bounds.getSize(new THREE.Vector3())
    const maxDim = Math.max(size.x, size.y, size.z) || 1
    clone.position.sub(center)
    clone.scale.setScalar(1.72 / maxDim)
    clone.traverse((obj) => {
      if (obj instanceof THREE.Mesh) {
        obj.castShadow = true
        obj.receiveShadow = true
        obj.material = Array.isArray(obj.material)
          ? obj.material.map((m) => m.clone())
          : obj.material.clone()
      }
    })
    return clone
  }, [scene])
  return <primitive object={prepared} />
}
useGLTF.preload('/models/anatomical_heart_-_codominance.glb')

function VesselTube({ v, selected, onSelect, prob }: { v: Vessel; selected: boolean; onSelect: (id: ID) => void; prob?: number }) {
  const curve = useMemo(() => new THREE.CatmullRomCurve3(v.points.map(p => new THREE.Vector3(...p))), [v])
  const color = riskColor(prob)
  return <mesh onClick={e => { e.stopPropagation(); onSelect(v.id) }} onPointerOver={() => { document.body.style.cursor = 'pointer' }} onPointerOut={() => { document.body.style.cursor = 'default' }} castShadow>
    <tubeGeometry args={[curve, 56, v.branch ? (selected ? .014 : .009) : (selected ? .027 : .019), 10, false]}/>
    <meshPhysicalMaterial color={color} emissive={color} emissiveIntensity={selected ? .32 : .10} roughness={.27} metalness={.02} clearcoat={.45}/>
  </mesh>
}

function VeinNetwork() {
  const veins: [number, number, number][][] = [
    [[-.22,.48,.35],[-.36,.28,.35],[-.43,.02,.26],[-.30,-.25,.20]],
    [[.26,.38,.34],[.40,.18,.29],[.35,-.06,.24],[.18,-.30,.18]],
    [[-.08,.18,.40],[-.20,.02,.34],[-.18,-.20,.25]],
  ]
  return <group>{veins.map((points, i) => {
    const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)))
    return <mesh key={i}><tubeGeometry args={[curve, 36, .012, 8, false]}/><meshStandardMaterial color="#567fbd" roughness={.3} metalness={.02}/></mesh>
  })}</group>
}

function ArteryInterior({ prob }: { prob?: number }) {
  const narrowing = prob === undefined ? .12 : Math.max(.06, Math.min(.72, prob * .7))
  return <group rotation={[0,0,Math.PI/2]}>
    <mesh><cylinderGeometry args={[.42,.42,2.3,64,1,true]}/><meshPhysicalMaterial color="#cf7b85" transparent opacity={.32} side={THREE.DoubleSide} depthWrite={false}/></mesh>
    <mesh><cylinderGeometry args={[.34,.34,2.31,64,1,true]}/><meshStandardMaterial color="#b84455" side={THREE.BackSide} transparent opacity={.55}/></mesh>
    <mesh position={[0,-.12,0]}><torusGeometry args={[.34,.34*narrowing,18,64,Math.PI*1.2]}/><meshStandardMaterial color="#e5b84f" roughness={.42}/></mesh>
    <mesh position={[0,-.12,0]}><sphereGeometry args={[.34*narrowing,24,16]}/><meshStandardMaterial color="#dca943" roughness={.65}/></mesh>
    {Array.from({length:8},(_,i)=><mesh key={i} position={[0,-.82+i*.22,0]}><sphereGeometry args={[.035,10,10]}/><meshStandardMaterial color="#f76c78" emissive="#9c1e30" emissiveIntensity={.18}/></mesh>)}
  </group>
}

export default function HeartScene({ selected, onSelect, probabilities = {}, focus = false, beating = true }: { selected: ID; onSelect: (id: ID) => void; probabilities?: Partial<Record<ID, number>>; focus?: boolean; beating?: boolean }) {
  return <div className="heart-canvas">
    <Canvas camera={{ position: [0, .02, 3.15], fov: 40 }} dpr={[1, 1.35]} gl={{ antialias: true, powerPreference: 'high-performance', alpha: false }} shadows>
      <color attach="background" args={['#f2f6fa']}/>
      <ambientLight intensity={1.15}/>
      <directionalLight position={[3,4,5]} intensity={2.2} castShadow shadow-mapSize-width={1024} shadow-mapSize-height={1024}/>
      <directionalLight position={[-3,1,-2]} intensity={.75} color="#9ac7df"/>
      <pointLight position={[-2,-1,3]} intensity={.55} color="#ffd4ce"/>
      <Suspense fallback={<Html center><span style={{fontSize:12,color:'#52657a'}}>Preparing 3D anatomy…</span></Html>}>
        {focus ? <ArteryInterior prob={probabilities[selected]}/> : <group rotation={[.02,-.16,0]}>
          <AnatomicalHeartModel/>
          {vessels.map(v => <VesselTube key={v.key} v={v} selected={selected===v.id} onSelect={onSelect} prob={probabilities[v.id]}/>)}
        </group>}
      </Suspense>
      <OrbitControls enablePan enableDamping dampingFactor={.08} rotateSpeed={.7} zoomSpeed={.85} minDistance={focus?1.5:1.7} maxDistance={focus?5:5.5}/>
    </Canvas>
    <div className="scene-hint">Anatomical model · Drag to rotate · Scroll to zoom · Vessel overlays are illustrative</div>
    <div className="scene-selected">{focus ? 'Illustrative vessel cross-section — NOT CT-derived' : `${selected} · ${probabilities[selected] === undefined ? 'No patient prediction' : (probabilities[selected]! * 100).toFixed(1) + '% model score'}`}</div>
  </div>
}
