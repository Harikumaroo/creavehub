export default function BackgroundBlobs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0" aria-hidden>
      <div className="bg-blob anim-blob" style={{ width:520,height:520,top:-150,right:-90,
        background:'radial-gradient(circle, rgba(232,71,10,0.19) 0%, transparent 70%)' }} />
      <div className="bg-blob anim-blob-r" style={{ width:400,height:400,bottom:-90,left:-70,
        background:'radial-gradient(circle, rgba(242,101,34,0.14) 0%, transparent 70%)' }} />
      <div className="bg-blob anim-blob-slow" style={{ width:300,height:300,top:'42%',left:'26%',
        background:'radial-gradient(circle, rgba(90,40,180,0.1) 0%, transparent 70%)' }} />
    </div>
  )
}
