/****** Object:  Table [dbo].[server]    Script Date: 2018/8/23 15:32:39 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[server](
	[IP] [nvarchar](50) NULL,
	[date] [datetime] NULL,
	[name] [nvarchar](50) NULL,
	[opentime] [datetime] NULL,
	[cpurate] [decimal](18, 2) NULL,
	[mem] [decimal](18, 2) NULL,
	[memrate] [decimal](18, 2) NULL,
	[netsent] [decimal](18, 2) NULL,
	[netspkg] [decimal](18, 2) NULL,
	[netrecv] [decimal](18, 2) NULL,
	[netrpkg] [decimal](18, 2) NULL,
	[diskname1] [nvarchar](50) NULL,
	[diskvol1] [decimal](18, 2) NULL,
	[diskfree1] [decimal](18, 2) NULL,
	[diskrate1] [decimal](18, 2) NULL,
	[diskname2] [nvarchar](50) NULL,
	[diskvol2] [decimal](18, 2) NULL,
	[diskfree2] [decimal](18, 2) NULL,
	[diskrate2] [decimal](18, 2) NULL,
	[diskname3] [nvarchar](50) NULL,
	[diskvol3] [decimal](18, 2) NULL,
	[diskfree3] [decimal](18, 2) NULL,
	[diskrate3] [decimal](18, 2) NULL,
	[diskname4] [nvarchar](50) NULL,
	[diskvol4] [decimal](18, 2) NULL,
	[diskfree4] [decimal](18, 2) NULL,
	[diskrate4] [decimal](18, 2) NULL,
	[diskname5] [nvarchar](50) NULL,
	[diskvol5] [decimal](18, 2) NULL,
	[diskfree5] [decimal](18, 2) NULL,
	[diskrate5] [decimal](18, 2) NULL,
	[password] [nvarchar](50) NULL
) ON [PRIMARY]

GO

