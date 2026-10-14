import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import { Suspense, useMemo, useRef } from 'react'
import * as THREE from 'three'

type ID='LAD'|'LCX'|'RCA'
type Vessel={key:string;id:ID;name:string;points:[number,number,number][];branch?:boolean}
const vessels:Vessel[]=[
{key:'lad-main',id:'LAD',name:'Left anterior descending',points:[[0.02,.68,.34],[.16,.48,.42],[.17,.21,.47],[.09,-.12,.43],[-.08,-.55,.26]]},
{key:'lad-diagonal',id:'LAD',name:'LAD diagonal branch',branch:true,points:[[.16,.36,.44],[.31,.22,.39],[.36,.04,.31]]},
{key:'lad-septal',id:'LAD',name:'LAD septal branch',branch:true,points:[[.13,.16,.46],[.02,.04,.45],[-.02,-.12,.40]]},
{key:'lcx-main',id:'LCX',name:'Left circumflex',points:[[0.02,.68,.34],[-.18,.54,.38],[-.39,.36,.33],[-.52,.11,.20],[-.39,-.18,.10]]},
{key:'lcx-om',id:'LCX',name:'Obtuse marginal branch',branch:true,points:[[-.37,.32,.32],[-.25,.13,.36],[-.15,-.04,.31]]},
{key:'rca-main',id:'RCA',name:'Right coronary artery',points:[[.1,.59,.30],[.37,.47,.29],[.53,.19,.22],[.46,-.10,.20],[.25,-.39,.15]]},
{key:'rca-pda',id:'RCA',name:'Posterior descending branch',branch:true,points:[[.46,-.10,.20],[.28,-.27,.24],[.05,-.38,.22],[-.12,-.45,.17]]}]
const riskColor=(p?:number)=>p===undefined?'#5b9fba':p>=.65?'#e45b68':p>=.35?'#e8a13b':'#18a782'
function VesselTube({v,selected,onSelect,prob}:{v:Vessel;selected:boolean;onSelect:(id:ID)=>void;prob?:number}){
 const curve=useMemo(()=>new THREE.CatmullRomCurve3(v.points.map(p=>new THREE.Vector3(...p))),[v]);const color=riskColor(prob)
 return <mesh onClick={e=>{e.stopPropagation();onSelect(v.id)}} onPointerOver={()=>document.body.style.cursor='pointer'} onPointerOut={()=>document.body.style.cursor='default'}>
 <tubeGeometry args={[curve,64,v.branch ? (selected ? 0.018 : 0.012) : (selected ? 0.032 : 0.020),12,false]}/><meshStandardMaterial color={color} emissive={color} emissiveIntensity={selected ? 0.55 : 0.15} roughness={.28}/></mesh>
}
function Pulse({enabled}:{enabled:boolean}){const ref=useRef<THREE.Group>(null);useFrame(({clock})=>{if(ref.current&&enabled){const s=1+Math.sin(clock.elapsedTime*3.8)*.025;ref.current.scale.setScalar(s)}});return <group ref={ref}>
 <mesh scale={[.54,.70,.35]} rotation={[0,0,-.18]}><sphereGeometry args={[1,48,48]}/><meshPhysicalMaterial color="#cb727c" roughness={.62} transparent opacity={.92}/></mesh>
 <mesh position={[-.19,.48,.02]} rotation={[0,0,-.3]}><capsuleGeometry args={[.15,.34,8,20]}/><meshStandardMaterial color="#c96b78"/></mesh>
 <mesh position={[.18,.50,.02]} rotation={[0,0,.25]}><capsuleGeometry args={[.14,.34,8,20]}/><meshStandardMaterial color="#e49a9d"/></mesh>
 <mesh position={[.0,.83,-.02]} rotation={[0,0,.2]}><cylinderGeometry args={[.12,.17,.42,24]}/><meshStandardMaterial color="#ae5667"/></mesh>
 </group>}
function ArteryInterior({prob}:{prob?:number}){const narrowing=prob===undefined ? 0.12 :Math.max(.06,Math.min(.72,prob*.7));return <group rotation={[0,0,Math.PI/2]}>
 <mesh><cylinderGeometry args={[.42,.42,2.3,64,1,true]}/><meshPhysicalMaterial color="#cf7b85" transparent opacity={.35} side={THREE.DoubleSide} depthWrite={false}/></mesh>
 <mesh><cylinderGeometry args={[.34,.34,2.31,64,1,true]}/><meshStandardMaterial color="#d34557" side={THREE.BackSide} transparent opacity={.55}/></mesh>
 <mesh position={[0,-.12,0]}><torusGeometry args={[.34,.34*narrowing,18,64,Math.PI*1.2]}/><meshStandardMaterial color="#e5c46b" roughness={.5}/></mesh>
 {Array.from({length:9},(_,i)=><mesh key={i} position={[0,-.85+i*.22,0]}><sphereGeometry args={[.045,10,10]}/><meshStandardMaterial color="#f76c78" emissive="#9c1e30" emissiveIntensity={.25}/></mesh>)}
 </group>}
export default function HeartScene({selected,onSelect,probabilities={},focus=false,beating=true}:{selected:ID;onSelect:(id:ID)=>void;probabilities?:Partial<Record<ID,number>>;focus?:boolean;beating?:boolean}){
 return <div className="heart-canvas"><Canvas camera={{position:[0,0,3.15],fov:42}} dpr={[1,1.7]}><color attach="background" args={['#f4f8fb']}/><ambientLight intensity={1.5}/><directionalLight position={[3,4,5]} intensity={2.1}/><pointLight position={[-3,-2,3]} intensity={.5}/><Suspense fallback={<Html center>Loading viewer…</Html>}>
 {focus?<ArteryInterior prob={probabilities[selected]}/>:<group rotation={[.05,-.16,0]}><Pulse enabled={beating}/>{vessels.map(v=><VesselTube key={v.key} v={v} selected={selected===v.id} onSelect={onSelect} prob={probabilities[v.id]}/>)}</group>}
 </Suspense><OrbitControls enablePan enableDamping minDistance={focus?1.5:1.7} maxDistance={focus?5:5.5}/></Canvas>
 <div className="scene-hint">Drag to rotate 360° · Scroll to zoom · Right-drag to pan</div><div className="scene-selected">{focus?'Illustrative vessel cross-section — NOT CT-derived':`${selected} · ${probabilities[selected]===undefined?'No patient prediction':(probabilities[selected]! *100).toFixed(1)+'% model score'}</div></div>
}
