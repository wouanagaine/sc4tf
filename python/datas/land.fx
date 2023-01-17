// Sample effect file

// transformations
float4x4 WorldViewProj : WORLDVIEWPROJECTION;

texture landTex1 < string name = "datas/wired.bmp"; >;

float texSizeX = 769;
float texSizeY = 769;

sampler land1 = sampler_state 
{
    texture = <landTex1>;
    AddressU  = WRAP;        
    AddressV  = WRAP;
    AddressW  = WRAP;
    MIPFILTER = POINT;
    MINFILTER = POINT;
    MAGFILTER = POINT;
};


struct VS_COMBINE3
{
    float4 Pos  : POSITION;
    float4 diffuse : COLOR0;
    float2 texDetColor : TEXCOORD0;
};

VS_COMBINE3 CombineVS3( float4 Pos : POSITION, float2 texColor : TEXCOORD0, float4 color : COLOR0 )
{
    VS_COMBINE3 output = (VS_COMBINE3)0;
    output.Pos = mul(Pos, WorldViewProj);    // position (view space)    
    
	  output.diffuse = color;
    output.texDetColor = float2( .5, Pos.y/5 ); 

    return output;
}

float4 CombinePS3( VS_COMBINE3 In ) : COLOR0
{
    float4 color = (2*In.diffuse)*tex2D( land1, In.texDetColor );
    return color;   
}

technique tec
{
    pass p0
    {
        alphablendenable = false;
		    CullMode = CW;
        VertexShader = compile vs_1_1 CombineVS3();
        PixelShader = compile ps_1_1 CombinePS3();
    }
}

technique FP
{
  pass p0
  {
    lighting = false;
    colorvertex=true;
    EMISSIVEMATERIALSOURCE=color1;
    cullmode=cw;
    texture[0]=<landTex1>;
    ColorArg1[0]=CURRENT;
    ColorArg2[0]=TEXTURE;
    ColorOp[0]=MODULATE;
    
  }
}
