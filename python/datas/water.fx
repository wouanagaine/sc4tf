// Sample effect file

// transformations
float4x4 WorldViewProj : WORLDVIEWPROJECTION;

texture landTex0 < string name = "datas/water.bmp"; >;

float texSizeX = 769;
float texSizeY = 769;



sampler water = sampler_state 
{
    texture = <landTex0>;
    AddressU  = WRAP;        
    AddressV  = WRAP;
    AddressW  = WRAP;
    MIPFILTER = LINEAR;
    MINFILTER = LINEAR;
    MAGFILTER = LINEAR;
};


struct VS_COMBINE
{
    float4 Pos  : POSITION;
    float2 texColor : TEXCOORD0;
};


VS_COMBINE CombineVS( float4 Pos : POSITION )
{
    VS_COMBINE output = (VS_COMBINE)0;
    output.Pos = mul(Pos, WorldViewProj);    // position (view space)    

    output.texColor = float2( Pos.x/(12*20), Pos.z/(12*20) ); 

    return output;
}


float4 CombinePS( VS_COMBINE In ) : COLOR0
{
    float4 color = tex2D( water, In.texColor );
    //return float4( color.r,color.g,color.b*4,.5);   
    return color;
}

technique tec
{
    pass p0
    {
        alphablendenable = true;
        srcblend = srcalpha;
        destblend = invsrcalpha;
		//FillMode=WireFrame;
		CullMode = None;
        VertexShader = compile vs_1_1 CombineVS();
        PixelShader = compile ps_1_1 CombinePS();
    }
}





technique FP
{
  pass p0
  {
    alphablendenable = true;
    srcblend = srcalpha;
    destblend = invsrcalpha;
    lighting = false;
    colorvertex=false;
    cullmode=None;
    texture[0]=<landTex0>;
    ColorArg1[0]=TEXTURE;
    ColorOp[0]=selectArg1;
    
  }
}


