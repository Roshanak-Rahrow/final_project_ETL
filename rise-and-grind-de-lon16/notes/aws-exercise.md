# AWS Exercises

## EC2

You're going to setup your own EC2 server, then extend it so that we can host a basic website on it. After that we will look at how we can tighten security of our instances.

Before beginning, make sure the region dropdown at the top of the screen is set to Ireland (eu-west-1).

### Security Group Setup

Before creating your own EC2 instance, you will need to create a [security group](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/working-with-security-groups.html). Security groups take control of the traffic that is allowed in and out of your instance. You can apply restrictions on port ranges and IP ranges. We will be restricting `SSH` access to your IP, but open `HTTP` to the world. This is bad practice, and so you would normally be much more restrictive in terms of what you allow in and out, but for the sake and simplicity of this exercise, we won't need to worry about that.

1. Go to `EC2` page by using the search bar
1. On the left-hand side under `Network & Security`,
    1. select `Security Groups`
    1. and then select `Create security group`
1. Give your security group a unique name (e.g. `your-name-sg`) and a description (e.g. `Your-Name SG`)
1. Change the VPC to the `RedshiftVPC`
    1. Delete the contents of the `VPC` box - it should then offer you a dropdown list - select `RedshiftVPC`
    1. If not, type `Red` in the box - it should find the one named `RedshiftVPC`
1. Under `Inbound rules`, select `Add rule`
    1. Rule 1: Select `SSH` for `Type` and `My IP` for `Source`
    1. Rule 2: Select `HTTP` for `Type` and input `0.0.0.0/0` in the text field to the right of `Source` and `Anywhere-IPv4` for `Source`
1. Under `Outbound rules`,
    1. Rule 1: Select `HTTP` as the type and input `0.0.0.0/0` in the text field to the right of `Destination`
    1. Rule 2: Select `HTTPS` as the type and input `0.0.0.0/0` in the text field to the right of `Destination`
1. Under the Tags section add a tag with key `Name` and value `your-name-sg`
1. Select `Create security group` to finish

### EC2 Instance Setup

Now let's set an instance up.

1. Go to EC2 and select `Launch Instance`
1. In the `Names and tags` section,
    1. add a name for your EC2 instance ( e.g `Your-Name Web Server`)
1. In the `Application and OS Images` section,
    1. select `Amazon Linux 2023 AMI`
1. In the `Instance type` section,
    1. select an instance type of `t2.micro`
1. In the `Key pair` section,
    1. Click on the `Create new key pair` link, a pop up dialogue will appear
    1. Do so by entering a key pair name (e.g  `yourname-key`)
    1. Keep key file format as .pem and click the `Create key pair` button
    1. The key will download automatically to you downloads folder
    1. The popup will close
    1. Move the downloaded key file `yourname-key.pem` into a suitable directory
        1. **DO NOT** put this in any Git folder - this would be like adding a password to git, but worse, which is **VERY BAD**
    1. The name should autofill in the `Key pair` section
1. In the `Network Settings` section,
    1. Click the `Edit` button on the right hand side
    1. Change the `VPC` to `RedshiftVPC`
    1. And use the Subnet dropdown to change it to the `RedshiftPublicSubnet0` subnet
    1. Under `Auto-assign Public IP`, select `Enable`
    1. Under `Firewall(security group)`, select `Existing security group`
    1. Under `Firewall(security group)`, use the Security groups dropdown to select the security group, you created earlier (e.g `your-name-sg`)
1. In the `Configure storage` section,
    1. Click the `Advanced` link on the top right
    1. Click the drop-down arrow next to `Volume 1`
    1. Under `Encrypted` select `Encrypted` from the dropdown
    1. Leave everything else as is!
1. In the `Advanced details` section,
    1. Change the `IAM Instance profile` to `de-academy-ec2-role`
    1. Do not touch any other settings here
1. Click on the orange button on the right hand side, to `Launch instance`
1. Navigate to `Instances` and select the `Instance ID` value of your instance
1. Wait for your instance to have an instance state of `Running` before moving on
    1. This should only take about 30 seconds

### Accessing the Instance

Your instance has now been spun up and is ready to be accessed. Let's see how we can go about getting inside it:

1. On your instance summary page, select `Connect` in the top-right of the webpage
1. Select the `SSH Client` tab and copy the long `ssh` command under `Example:`

Now follow the below steps on your terminal (use `wsl` if on Windows):

1. Open a terminal in the folder your downloaded key file is in e.g. `yourname-key.pem`
1. Run: `chmod 400 {name-of-key}.pem`
1. Paste the `ssh` command you copied and hit enter
1. You will be asked `Are you sure you want to continue connecting (yes/no/[fingerprint])?`, type `yes` and hit enter
1. You should now be logged in!
    1. Your terminal prompt should change to show you are inside the instance!

### Setting up the website

1. Elevate your privileges by running: `sudo su`
1. Update all of the packages on the instance: `yum update -y`
1. Install an apache webserver: `yum install httpd -y`
1. Change directory to /var/www/html with `cd /var/www/html`
1. Run `nano index.html`, copy/paste the contents of the `index.html` handout and save the file
    1. To copy the contents you need to open the `index.html` file with a text editor to get the html from it
1. Start the webserver: `service httpd start`
1. Configure the web server to restart if it gets stopped: `chkconfig on`
1. Copy the IP address of your instance, you can find it under `Public IPv4 address` on the instance page in AWS.
1. Paste the address into your browser and watch the magic happen... Hope you like it 😉

**Note**: If you can't browse to it and you are using Chrome (or similar), it will try to default to `https:xxx`. This won't work, so change the URL to `http:xxx` instead.

### Extending our security

The problem with our current setup is that we're relying on having a key file on our machine. Think about the below:

- What if we lose the key?
- What if the key is leaked online?
- What if someone at a company leaves, how do we safely transfer the key?
- What if multiple people want to access the EC2 instance, how would they safely distribute the key?

Is there a way we can login to our instance without needing to worry about keys? We can with a tool called `SSM Agent`.

`SSM Agent` is Amazon software that can be installed and configured on an EC2 instance. This will remove the need for us to use a key to access our instance. This works by configuring and ensuring the correct people are accessing it with IAM policies and roles. It also means we can close off port 22 inbound access so we increase security even further.

After setting up our EC2 instance so it has the correct permissions to communicate with SSM, we could access our instance without SSH or a .pem key as follows:

1. Copy your EC2 instance ID
1. Run the command `aws ssm start-session --target [instance_id] --profile [name_of_profile] --region eu-west-1`

Using SSM lets AWS do all the legwork for applying security restrictions as opposed to putting that on the user. We won't go over manually configuring SSM in this session, but this approach would be preferred over direct SSH access on a real world project.

### Wrapping up

When you are done with this part of the exercise, please delete the following:

1. Any EC2 instances you created
1. Any security groups you created
1. The `.pem` file you downloaded

---

