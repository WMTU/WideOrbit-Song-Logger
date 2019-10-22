package fm.wmtu;

// import java utilities
import java.awt.Color;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Properties;
import java.util.Set;


// import UI elements
import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JTextField;

// import libraries
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.apache.commons.text.WordUtils;

// import wideorbit libraries
import com.google.ras.api.core.plugin.BasicWidget;
import com.google.ras.api.core.ui.resources.PackageResources;
import com.google.ras.api.core.ui.resources.Resources;

public class DiscrepancyWidget extends BasicWidget implements ActionListener 
{
	private static final Resources R = 
			new PackageResources( DiscrepancyWidget.class );
	private static final Insets WEST_INSETS = new Insets( 5, 10, 5, 10 );
	private static final Insets EAST_INSETS = new Insets( 5, 10, 5, 10 );
	private static final String QUERY = "INSERT INTO discrepency_logs "
			+ "(dj_name, song_name, artist, word, hit_button) VALUES "
			+ "(?, ?, ?, ?, ?)";
	
	private JLabel messageLabel;
	private JLabel yourNameLabel;
	private JTextField yourName;
	private JLabel songTitleLabel;
	private JTextField songTitle;
	private JLabel songArtistLabel;
	private JTextField songArtist;
	private JLabel badWordLabel;
	private JTextField badWord;
	private JLabel buttonLabel;
	private JRadioButton buttonYes;
	private JRadioButton buttonNo;
	
	private String errorMessage;
	
	public DiscrepancyWidget() throws FileNotFoundException, IOException
	{
		super( "Discrepancy", R.getImage("DiscrepancyWidget.png") );

		// Load config file
		InputStream input = getClass().getClassLoader().getResourceAsStream( "config.properties" );
		if ( input == null )
		  throw new FileNotFoundException( "Widget configuration file not found in the classpath" );

		// Load properties into new config object
		Properties config = new Properties();
		config.load( input );
		log_endpoint  = config.getProperty( "log_endpoint" );
		log_key       = config.getProperty( "log_key" );
		input.close();
	}
	
	@Override
	protected JComponent buildContentPanel() 
	{
		getToolbar().setTitle( "Discrepancy Log" );
		
		// Set up container JPanel
		JPanel panel = new JPanel();
		panel.setBackground( Color.BLACK );
		panel.setLayout( new GridBagLayout() );
		
		// Initialize object variables
		GridBagConstraints gbc;
		Font newLabelFont;
		
		// Add message label
		gbc = createGbc( 0, 0 );
		gbc.gridwidth = 3;
		gbc.anchor = GridBagConstraints.CENTER;
		gbc.insets = new Insets( 10, 10, 10, 10 );
		gbc.weightx = 1.0;
		messageLabel = new JLabel( " ", JLabel.CENTER );
		messageLabel.setForeground( Color.WHITE );
		panel.add( messageLabel, gbc );
		
		// Add your name label and field
		gbc = createGbc( 0, 1 );
		yourNameLabel = new JLabel( "Your Full Name", JLabel.RIGHT );
		yourNameLabel.setForeground( new Color( 65, 227, 195 ) );
		newLabelFont = new Font( yourNameLabel.getFont().getName(), 
				Font.BOLD + Font.ITALIC, yourNameLabel.getFont().getSize() );
		yourNameLabel.setFont(newLabelFont);
		panel.add( yourNameLabel, gbc );
		gbc = createGbc( 1, 1 );
		yourName = new JTextField( 27 );
		panel.add( yourName, gbc );
		
		// Add song title label and field
		gbc = createGbc( 0, 2 );
		songTitleLabel = new JLabel( "Song Name", JLabel.RIGHT );
		songTitleLabel.setForeground( new Color( 255, 243, 53 ) );
		newLabelFont = new Font( songTitleLabel.getFont().getName(), 
				Font.BOLD + Font.ITALIC, songTitleLabel.getFont().getSize() );
		songTitleLabel.setFont(newLabelFont);
		panel.add( songTitleLabel, gbc );
		gbc = createGbc( 1, 2 );
		songTitle = new JTextField( 27 );
		panel.add( songTitle, gbc );
		
		// Add artist label and field
		gbc = createGbc( 0, 3 );
		songArtistLabel = new JLabel( "Artist or Group", JLabel.RIGHT );
		songArtistLabel.setForeground( new Color( 235, 124, 43 ) );
		newLabelFont = new Font( songArtistLabel.getFont().getName(), 
				Font.BOLD + Font.ITALIC, songArtistLabel.getFont().getSize() );
		songArtistLabel.setFont(newLabelFont);
		panel.add( songArtistLabel, gbc );
		gbc = createGbc( 1, 3 );
		songArtist = new JTextField( 27 );
		panel.add( songArtist, gbc );
		
		// Add bad word label and field
		gbc = createGbc( 0, 4 );
		badWordLabel = new JLabel( "What word was said?", JLabel.RIGHT );
		badWordLabel.setForeground( new Color( 219, 45, 235 ) );
		newLabelFont = new Font( badWordLabel.getFont().getName(), 
				Font.BOLD + Font.ITALIC, badWordLabel.getFont().getSize() );
		badWordLabel.setFont(newLabelFont);
		panel.add( badWordLabel, gbc );
		gbc = createGbc( 1, 4 );
		badWord = new JTextField( 27 );
		panel.add( badWord, gbc );
		
		// Add button hit boxes and field
		gbc = createGbc( 0, 5 );
		buttonLabel = new JLabel( "Did you hit the swear button?", 
				JLabel.RIGHT );
		buttonLabel.setForeground( new Color( 227, 6, 48 ) );
		newLabelFont = new Font( buttonLabel.getFont().getName(), 
				Font.BOLD + Font.ITALIC, buttonLabel.getFont().getSize() );
		buttonLabel.setFont(newLabelFont);
		panel.add( buttonLabel, gbc );
		ButtonGroup buttons = new ButtonGroup();
		gbc = createGbc( 1, 5 );
		gbc.anchor = GridBagConstraints.WEST;
		gbc.gridwidth = 1;
		gbc.weightx = 0.2;
		buttonYes = new JRadioButton( "Yes" );
		buttonYes.setForeground( Color.WHITE );
		buttons.add( buttonYes );
		panel.add( buttonYes, gbc );
		gbc = createGbc( 2, 5 );
		gbc.anchor = GridBagConstraints.WEST;
		gbc.gridwidth = 1;
		gbc.weightx = 0.8;
		buttonNo = new JRadioButton( "No" );
		buttonNo.setForeground( Color.WHITE );
		buttons.add( buttonNo );
		panel.add( buttonNo, gbc );
		
		// Add buttons
		gbc = createGbc( 0, 6 );
		gbc.fill = GridBagConstraints.NONE;
		JButton addLog = new JButton( "Add Log" );
		addLog.setActionCommand( "submit" );
		addLog.addActionListener( this );
		panel.add( addLog, gbc );
		gbc = createGbc( 1, 6 );
		gbc.anchor = GridBagConstraints.WEST;
		gbc.fill = GridBagConstraints.NONE;
		JButton clearForm = new JButton( "Clear Form" );
		clearForm.setActionCommand( "clear" );
		clearForm.addActionListener( this );
		panel.add( clearForm, gbc );
		
		return panel;
	}
	
	private GridBagConstraints createGbc( int x, int y ) 
	{
		GridBagConstraints gbc = new GridBagConstraints();
		gbc.gridx = x;
		gbc.gridy = y;
		gbc.gridwidth = (x == 0) ? 1 : 2;
		gbc.gridheight = 1;

		gbc.anchor = GridBagConstraints.EAST;
		gbc.fill = (x == 0) ? GridBagConstraints.BOTH
				: GridBagConstraints.HORIZONTAL;

		gbc.insets = (x == 0) ? WEST_INSETS : EAST_INSETS;
		gbc.weightx = (x == 0) ? 0.1 : 1.0;
		gbc.weighty = 1.0;
		return gbc;
	}

	@Override
	public void actionPerformed(ActionEvent event) 
	{
		if ( event.getActionCommand().equals( "submit" ) ) 
		{
			if ( yourName.getText().trim().equals( "" ) ) 
			{
				messageLabel.setText( "Error: 'Your Full Name' cannot be "
						+ "blank" );
				messageLabel.setForeground( Color.ORANGE );
				return;
			}
			if ( songTitle.getText().trim().equals( "" ) ) 
			{
				messageLabel.setText( "Error: 'Song Name' cannot be blank" );
				messageLabel.setForeground( Color.ORANGE );
				return;
			}
			if ( songArtist.getText().trim().equals( "" ) ) 
			{
				messageLabel.setText( "Error: 'Artist or Group' cannot be blank" );
				messageLabel.setForeground( Color.ORANGE );
				return;
			}
			if ( badWord.getText().trim().equals( "" ) ) 
			{
				messageLabel.setText( "Error: 'What word was said?' cannot be blank" );
				messageLabel.setForeground( Color.ORANGE );
				return;
			}
			if ( !( buttonYes.isSelected() || buttonNo.isSelected() ) ) 
			{
				messageLabel.setText( "Error: 'Did you hit the swear button?' must be specified" );
				messageLabel.setForeground( Color.ORANGE );
				return;
			}
			
			String regex = "(<([^>]+)>)";
			String name = yourName.getText().replaceAll( regex, "" );
			String song = songTitle.getText().replaceAll( regex, "" );
			String artist = songArtist.getText().replaceAll( regex, "" );
			String word = badWord.getText().replaceAll( regex, "" );
			String button = ( buttonYes.isSelected() ) ? "yes" : "no";
			
			artist = WordUtils.capitalizeFully( artist );
			song = WordUtils.capitalizeFully( song );
			
			boolean success = sendLog( name, song, artist, word, button );
			
			if ( success ) 
			{
				Date rightNow = new Date();
				SimpleDateFormat dateFormat = 
						new SimpleDateFormat( "h:mm a EEE',' MMM'.' d" );
				messageLabel.setText( "Thank you! " + 
						dateFormat.format( rightNow ) );
				messageLabel.setForeground( Color.GREEN );
				
				// Clear form fields
				yourName.setText( "" );
				songTitle.setText( "" );
				songArtist.setText( "" );
				badWord.setText( "" );
				buttonYes.setSelected( false );
				buttonNo.setSelected( false );
			} 
			else 
			{
				messageLabel.setText( "Error: " + errorMessage );
				messageLabel.setForeground( Color.RED );
			}
		} 
		else if ( event.getActionCommand().equals( "clear" ) ) 
		{
			messageLabel.setText( " " );
			yourName.setText( "" );
			songTitle.setText( "" );
			songArtist.setText( "" );
			badWord.setText( "" );
			buttonYes.setSelected( false );
			buttonNo.setSelected( false );
		}
	}
	
	private boolean sendLog( String name, String song, String artist, String word, String buttonHit ) 
	{
		try {
			URL url = new URL( log_endpoint );
	  
			// Build map of request parameters
			Map<String, Object> params = new LinkedHashMap<String, Object>();
			params.put( "api_key", log_key);
			params.put( "song", song );
			params.put( "artist", artist );
			params.put( "dj_name", name );
			params.put( "word", word );
			params.put( "button_hit", buttonHit );
	  
			// Form request body from parameter map
			StringBuilder postData = new StringBuilder();
			postData.append( '{' );
			for ( Map.Entry<String, Object> param : params.entrySet() ) 
			{
			  if ( postData.length() != 1 )
				postData.append( ',' );
			  postData.append( '"' );
			  postData.append( param.getKey() );
			  postData.append( '"' );
			  postData.append( ':' );
			  postData.append( '"' );
			  postData.append( String.valueOf( param.getValue() ) );
			  postData.append( '"' );
			}
			postData.append( '}' );
			byte[] postDataBytes = postData.toString().getBytes( "UTF-8" );
	  
			// Initiate POST request to Log app
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod( "POST" );
			conn.setRequestProperty( "Content-Type", "application/json" );
			conn.setRequestProperty( "Content-Length", String.valueOf( postDataBytes.length ) );
			conn.setDoOutput( true );
			conn.getOutputStream().write( postDataBytes );
	  
			// Handle response from Log app
			int status = conn.getResponseCode();
			String message = conn.getResponseMessage();
			if ( status < 200 || status > 202 ) 
			{
			  errorMessage = String.format( "Log: HTTP %d: %s", status, message );
			  return false;
			}
		  } 
		  catch ( Exception e ) 
		  {
			errorMessage = ExceptionUtils.getStackTrace( e );
			e.printStackTrace();
			return false;
		  }
	  
		  return true;
	}
	
}
