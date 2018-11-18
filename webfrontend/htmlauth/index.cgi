#!/usr/bin/perl

# Einbinden der LoxBerry-Module
use CGI;
use LoxBerry::System;
use LoxBerry::Web;
use GD;

# Limit File-Upload to 5 MB
$CGI::POST_MAX = 1024 * 5000;

# Die Version des Plugins wird direkt aus der Plugin-Datenbank gelesen.
my $version = LoxBerry::System::pluginversion();
 
# Mit dieser Konstruktion lesen wir uns alle POST-Parameter in den Namespace R.
my $cgi = CGI->new;
$cgi->import_names('R');
# Ab jetzt kann beispielsweise ein POST-Parameter 'form' ausgelesen werden mit $R::form.
 
 
# Wir Übergeben die Titelzeile (mit Versionsnummer), einen Link ins Wiki und das Hilfe-Template.
# Um die Sprache der Hilfe brauchen wir uns im Code nicht weiter zu kümmern.
LoxBerry::Web::lbheader("External Link Plugin", "www.google.com", "help.html");
  

# Wir initialisieren unser Template. Der Pfad zum Templateverzeichnis steht in der globalen Variable $lbptemplatedir.

my $template = HTML::Template->new(
    filename => "$lbptemplatedir/index.html",
    global_vars => 1,
    loop_context_vars => 1,
    die_on_bad_params => 0,
	associate => $cgi,
);
  
# Jetzt lassen wir uns die Sprachphrasen lesen. Ohne Pfadangabe wird im Ordner lang nach language_de.ini, language_en.ini usw. gesucht.
# Wir kümmern uns im Code nicht weiter darum, welche Sprache nun zu lesen wäre.
# Mit der Routine wird die Sprache direkt ins Template übernommen. Sollten wir trotzdem im Code eine brauchen, bekommen
# wir auch noch einen Hash zurück.
my %L = LoxBerry::System::readlanguage($template, "language.ini");


# ---------------------------------------------------
# Build new Plugin
# ---------------------------------------------------
if ($R::btnBuild)
{
	my $PluginFolder = "lnk_$R::txtPluginFolder";
	my $PluginName = "$R::txtPluginName";
	my $PluginURL = "$R::txtPluginURL";
	my $procRet;
	my $PluginIcon = "$R::btnUploadIcon";
	my $uploadedIconHandle = $cgi->upload("btnUploadIcon");


        # copy template plugin folder
	system("cp -r $lbpdatadir/__tmplplugin__ /tmp/$PluginFolder");


	# write uploaded icon to /tmp/lnk_Name/icons/upload.png
	open ( UPLOADFILE, ">/tmp/$PluginFolder/icons/upload.png" ) or die "$!";
	binmode UPLOADFILE;
	while ( <$uploadedIconHandle> )
	{
		print UPLOADFILE;
	}
	close UPLOADFILE;


	# resize uploaded image to correct size
	my @IconSizes = ("512","256","128","64");
	foreach (@IconSizes)
	{
		my $uploadedIcon = newFromPng GD::Image("/tmp/$PluginFolder/icons/upload.png");
		my $icon = new GD::Image($_,$_);
		$icon->copyResized($uploadedIcon,0,0,0,0,$_,$_,$uploadedIcon->width,$uploadedIcon->height);
		open ( ICONFILE, ">/tmp/$PluginFolder/icons/icon_$_.png" ) or die "$!";
		binmode ICONFILE;
		print ICONFILE $icon->png;
		close ICONFILE;
	}


	# replace plugin name in files
	system("sed -i -e 's/##PLUGIN_NAME##/$PluginName/g' /tmp/$PluginFolder/plugin.cfg");
        system("sed -i -e 's/##PLUGIN_NAME##/$PluginName/g' /tmp/$PluginFolder/webfrontend/htmlauth/index.cgi");

	# replace plugin folder-name in files
        system("sed -i -e 's/##PLUGIN_FOLDER##/$PluginFolder/g' /tmp/$PluginFolder/plugin.cfg");

	# replace plugin URL in files
	system("sed -i -e 's|##PLUGIN_URL##|$PluginURL|g' /tmp/$PluginFolder/webfrontend/htmlauth/forward.html");

	print "(sed -i -e 's|##PLUGIN_URL##|$PluginURL|g' /tmp/$PluginFolder/webfrontend/htmlauth/forward.html) &";

	# create zip archive
	system("cd /tmp/$PluginFolder && zip -q -r /$lbphtmldir/$PluginFolder.zip ./*");

	# cleanup temp folder
	#system("(rm -rf /tmp/$PluginFolder)" );

	print "<br>DEBUG: http://loxberry.miklis-online.de/plugins/external-link/$PluginFolder.zip";	
}


# ---------------------------------------------------
# Control for "txtPluginName" Textfield
# ---------------------------------------------------
my $txtPluginName = $cgi->textfield(
      -name    => 'txtPluginName',
      -default => $L{'EXTERNAL-LINK.txtPluginName'},
  );
$template->param( txtPluginName => $txtPluginName );


# ---------------------------------------------------
# Control for "txtPluginFolder" Textfield
# ---------------------------------------------------
my $txtPluginFolder = $cgi->textfield(
      -name    => 'txtPluginFolder',
      -default => $L{'EXTERNAL-LINK.txtPluginFolder'},
  );
$template->param( txtPluginFolder => $txtPluginFolder );


# ---------------------------------------------------
# Control for "txtPluginURL" Textfield
# ---------------------------------------------------
my $txtPluginURL = $cgi->textfield(
     -name    => 'txtPluginURL',
     -default => $L{'EXTERNAL-LINK.txtPluginURL'},
  );
$template->param( txtPluginURL => $txtPluginURL );


# ---------------------------------------------------
# Control for "txtPluginURL" Textfield
# ---------------------------------------------------
my $btnUploadIcon = $cgi->filefield(
     -name    => 'btnUploadIcon',
     -default => $L{'EXTERNAL-LINK.btnUploadIcon'},
  );
$template->param( btnUploadIcon => $btnUploadIcon );


# ---------------------------------------------------
# Control for "frmStart" Form
# ---------------------------------------------------
my $frmStart = $cgi->start_form(
      -name    => 'ExternalPlugin',
      -enctype => &CGI::MULTIPART,
      -method => 'POST',
  );
$template->param( frmStart => $frmStart );


# ---------------------------------------------------
# Control for "frmEnd" Form
# ---------------------------------------------------
my $frmEnd = $cgi->end_form();
$template->param( frmEnd => $frmEnd );


# ---------------------------------------------------
# Control for "btnBuild" Button
# ---------------------------------------------------
my $btnBuild = $cgi->submit(
      -name    => 'btnBuild',
      -value => $L{'EXTERNAL-LINK.btnBuild'},
  );
$template->param( btnBuild => $btnBuild );


# ---------------------------------------------------
# Control for "btnReset" button
# ---------------------------------------------------
my $btnReset= $cgi->defaults(
      -name    => 'btnReset',
      -value => $L{'EXTERNAL-LINK.btnReset'},
  );
$template->param( btnReset => $btnReset );


# ---------------------------------------------------
# Localized Labels from language.ini
# ---------------------------------------------------
$template->param( lblPluginName => $L{'EXTERNAL-LINK.lblPluginName'} );
$template->param( lblPluginFolder => $L{'EXTERNAL-LINK.lblPluginFolder'} );
$template->param( lblPluginURL => $L{'EXTERNAL-LINK.lblPluginURL'}  );
$template->param( lblPluginIcon => $L{'EXTERNAL-LINK.lblPluginIcon'}  );
$template->param( btnUpload => $L{'EXTERNAL-LINK.btnUpload'}  );
$template->param( lblPluginZIP => $L{'EXTERNAL-LINK.lblPluginZIP'}  );
$template->param( txtDescription => $L{'EXTERNAL-LINK.txtDescription'}  );


# Nun wird das Template ausgegeben.
print $template->output();
  
# Schlussendlich lassen wir noch den Footer ausgeben.
LoxBerry::Web::lbfooter();
